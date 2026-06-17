#!/usr/bin/env python
import argparse
import re
import json

from collections import deque
from logging import WARNING, DEBUG
from pathlib import Path
from typing import Any, Iterable, Optional, Tuple
from traceback import format_exc

from bs4 import BeautifulSoup

_re_time = re.compile(
    r"^\s*(?P<raw_time>\d+\.\d+)(\+(?P<penalty>(dnf|dsq|off|out|rrn|\d+)).*)?\s*$"
)


class ResultsParseError(Exception):
    pass


class HeatsParseError(Exception):
    pass


def normalize_axware_entry(
    axware_raw_data: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Normalize native AxWare result column names"""
    base_entry = {
        "msrId": "",
        "email": "",
        "class": "",
        "carNumber": "",
        "driverName": "",
        "carModel": "",
        "carColor": "",
        "sponsor": "",
        "runs": [],
    }

    _axware_to_submit_map = {
        "Unique ID": "msrId",
        "Email #1": "email",
        "Class": "class",
        "#": "carNumber",
        "Driver": "driverName",
        "Car Model": "carModel",
        "Car Color": "carColor",
        "Sponsor": "sponsor",
    }

    out_data = [
        dict(
            base_entry,
            **{_axware_to_submit_map.get(k, k): v for k, v in entry.items()},
        )
        for entry in axware_raw_data
    ]

    return out_data


def parse_time(raw_value: Optional[str]) -> Optional[Tuple[float, int, str]]:
    try:
        if raw_value is not None and (match := _re_time.match(raw_value)):
            raw_time = float(match.group("raw_time"))
            penalty = match.group("penalty")

            # penalty overrides cones
            if penalty in ("dnf", "dsq", "off", "out", "rrn"):
                return (raw_time, 0, penalty)
            # penalty is just cones
            elif penalty:
                return (raw_time, int(penalty), "dirty")
            # clean run
            else:
                return (raw_time, 0, "clean")

        else:
            return None

    except Exception as e:
        raise RuntimeError(f"Unable to parse result `{raw_value}` ({str(e)})")


def parse_axware_live_results(
    fpath: Path,
) -> tuple[list[dict[str, Any]], list, dict[int, list[str]]]:
    """Returns all results in the event"""

    log_msgs = {
        DEBUG: [],
        WARNING: [],
    }

    try:

        s = None
        with open(fpath, "r", encoding="utf-8") as fp:
            s = BeautifulSoup(fp, "html.parser")

        if not s:
            raise ResultsParseError(f"Unable to parse raw HTML from {fpath.resolve()}")

    except:
        raise

    # parse real-time table if it exists
    realtime_runs = []
    try:
        realtime_table = next(
            filter(lambda x: "wdivs" in x.attrs.get("class", {}), s.find_all("table"))
        )

        realtime_rows = realtime_table.contents[
            0
        ].find_all(  # pyright: ignore[reportAttributeAccessIssue]
            lambda x: len(x.contents) > 3
        )
        header_row = realtime_rows[0]
        latest_run_iter = filter(lambda x: len(x.text) > 11, realtime_rows[1:])
        latest_runs = zip(latest_run_iter, latest_run_iter)

        headers = [h.string.strip() for h in header_row.find_all("th")]
        for row1, row2 in latest_runs:
            vals = [x.text.strip() for x in row1.find_all("td")]
            row_data = {k: v for k, v in zip(headers, vals)}

            entryClass, entryNum = row_data["Entry"].split()
            run = {
                "class": entryClass,
                "carNumber": entryNum,
                "driverName": row_data["Driver"],
                "carModel": row_data["Car Model"],
                "time": parse_time(row_data["Time"]),
            }

            realtime_runs.append(run)

    except:
        log_msgs[DEBUG].append("Unable to read real-time runs table")
        realtime_runs = []

    # get results table
    try:
        results_table = s.find_all("table")[-1]

        # filter out class line rules and get header/result rows
        filtered_rows = results_table.contents[
            0
        ].find_all(  # pyright: ignore[reportAttributeAccessIssue]
            lambda x: len(x.contents) > 3
        )
        header_row, result_rows = filtered_rows[0], filtered_rows[1:]

        # extract all headers
        headers = [t.string.strip() for t in header_row.find_all("th")]

        # check if results file is multirow formatted
        multirow = False
        for header in headers:
            if ".." in header:
                multirow = True
                break

    except:
        tb = format_exc()
        raise ResultsParseError(
            f"Unable to extract results table from AxWare HTM output\n\n{tb}"
        )

    # extract results
    results = []

    # only used for multirow mode
    current_entry = {}
    current_runs = []
    current_row = 0

    for row in result_rows:

        row_data = None

        try:
            row_data = row.find_all("td")
            entry = {}
            row_runs = []

            # extract all information from this row
            for header, raw_value in zip(headers, row_data):

                text = raw_value.text.strip()

                # parse times
                if "Run" in header:
                    value = parse_time(text)
                elif header == "Pax Time":
                    if value := parse_time(text):
                        value = value[0]

                # parse integers
                elif header == "Pos":
                    value = int(text.replace("T", ""))

                # all other values, just store raw string
                else:
                    value = text

                if "Run" in header:

                    # when parsing multirow results files, it's possible to have a case where an entry
                    # in a "Run" column doesn't actually correspond to an actual run. This can be
                    # detected by checking for a "valign" attribute in the raw tag
                    # skip appending the run value if the cell is actually just a placeholder
                    if "valign" not in raw_value.attrs:
                        continue

                    # ignore empty runs
                    if value is None:
                        continue

                    row_runs.append(value)

                else:
                    entry[header] = value

            # multi-row and/or multi-day, (multirow mode is guaranteed for multi-day)
            if multirow:
                # new entry, create new dictionary
                if row_data[0].text:

                    # add previous entry to output results
                    if current_entry:
                        results.append(current_entry)

                    current_entry = {}
                    current_entry.update(entry)
                    current_entry["Diff."] = None
                    current_entry["runs"] = {entry.get("Day", "Segment 1"): row_runs}
                    current_runs = row_runs
                    current_row = 0

                # next row for current entry, append runs to existing entry
                else:

                    # parsing failed before this row, move on to next row
                    if current_entry is None:
                        current_row += 1
                        continue

                    # in multiday-files, terminate previous day results when encountering next day row
                    if (
                        "Day" in entry
                        and entry["Day"]
                        and entry["Day"] not in current_entry["runs"]
                    ):
                        current_runs = []
                        current_entry["runs"][entry["Day"]] = current_runs

                    # diff is stored in "Total" column in second row when in multirow
                    if current_entry["Diff."] is None and current_row == 1:
                        current_entry["Diff."] = entry["Total"]

                    current_runs.extend(row_runs)

                current_row += 1

            # single row mode
            else:
                entry["runs"] = {"D1": row_runs}  # use default 'D1' for segment name
                results.append(entry)

        except Exception as e:
            log_msgs[WARNING].append(str(e))

            if row_data is not None:
                d = dict(zip(headers, [x.text for x in row_data]))
                log_msgs[WARNING].append(f"Failed parsing row data: {str(d)}")
            else:
                log_msgs[WARNING].append(f"Failed parsing row: {row.text}")

            current_entry = None
            continue

    # append final entry to results in multirow mode
    if multirow and current_entry is not None:
        last_segment = next(reversed(current_entry["runs"].keys()))
        current_entry["runs"][last_segment] = current_runs
        results.append(current_entry)

    return normalize_axware_entry(results), realtime_runs, log_msgs


def extract_heats_from_section(matches: Iterable[re.Match]) -> list[str]:
    data = []
    for m in matches:
        heat = int(m.group("heat"))
        data.append(
            [
                x.split("-")[0]
                for x in re.split(r"[\s\n]+", m.group("classes"))
                if len(x.split("-")) == 2
            ]
        )
    return data


def parse_axware_heats_txt(fpath: Path) -> dict[str, list[str]]:

    with open(fpath, "r", encoding="utf-8") as fp:
        ftext = fp.read()

    re_dividers = re.compile(r"-+\n")
    re_heat_info = re.compile(
        r"[\r\n][\t ]+(?P<heat>\d+)\s+(?:(?P<num_cars>\d+)\s+)?(?P<classes>(?:\s*?\w+-\d+[\t ]*\n?)+)",
        flags=re.MULTILINE,
    )

    sections = re_dividers.split(ftext)

    if len(sections) != 4:
        raise HeatsParseError("Invalid heats file format")

    run_section = sections[2]
    work_section = sections[3] if sections[3].strip() else None

    run_heat_matches = list(re_heat_info.finditer(run_section))

    # file only has run heats specified, assume work heats are rotated by one
    # e.g. 3 heats --> run order 1-2-3, work order 3-1-2
    if work_section is None:
        work_heat_matches = deque(run_heat_matches)
        work_heat_matches.rotate(-1)
    else:
        work_heat_matches = list(re_heat_info.finditer(work_section))

        if len(run_heat_matches) != len(work_heat_matches):
            raise HeatsParseError("Unequal number of work and run heats")

    out_data = {
        "run": extract_heats_from_section(run_heat_matches),
        "work": extract_heats_from_section(work_heat_matches),
    }

    return out_data


if __name__ == "__main__":
    argp = argparse.ArgumentParser(
        description="Simple parser to convert AxWare live results HTML file into JSON"
    )
    argp.add_argument("file", nargs="*", type=Path)

    args = argp.parse_args()

    for fpath in args.file:

        fpath: Path
        outdir = fpath.parent
        fname = fpath.stem

        results = None
        realtime_results = None

        if fpath.suffix == ".txt":
            results = parse_axware_heats_txt(fpath)
        else:
            results, realtime_results, log_msgs = parse_axware_live_results(fpath)

        outpath = fpath.with_suffix(".json")
        realtime_outpath = (outdir / f"{fname}_realtime").with_suffix(".json")

        if results:
            with open(outpath, "w") as fp:
                json.dump(results, fp, indent=4)

        if realtime_results:
            with open(realtime_outpath, "w") as fp:
                json.dump(realtime_results, fp, indent=4)
