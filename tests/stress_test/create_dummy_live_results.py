import random

from pathlib import Path
from math import floor
from time import sleep

# seed RNG
_seed = 'a-totally-random-seed'
random.seed(_seed)

# configure output
_num_drivers = 120
_num_runs = 20
_min_run_time = 50
_max_run_time = 80
_classes = ['n', 'int', 'es', 'mzst', 'er', 'hardo', 'pony', 'fwd']
_pax_classes = ['ss','as','bs','cs','ds','es','fs','gs','hs','hcs','ssc','sst','ast','bst','cst','dst','est','gst','ssp','asp','bsp','csp','dsp','esp','fsp','camt','camc','cams','xa','xb','xu','evx','xp','bp','cp','dp','ep','fp','hcr','smf','sm','ssm','csm','csx','am','bm','cm','dm','em','fm','fsae','km']
_refresh_rate_sec = 0.5
_input_template_fpath = Path(__file__).parent / 'results_base.htm'
_output_fpath = Path('C:/axware/results-live.htm')
_lowrow_flag = True

def get_row_type() -> str:
    global _lowrow_flag
    return 'low' if _lowrow_flag else 'high'

def format_run(run: dict[str, int | float | bool] | None) -> str:

    if run is None:
        outStr = ''
        
    else:

        outStr = f'{run["time"]:.3f}'

        if run['dnf']:
            outStr += '+dnf'
        elif run['cones'] > 0:
            outStr += f'+{run["cones"]:d}'

    return outStr
    
def generate_htm(data: dict[str, dict[str, list[dict[str, int|float|bool]]]]):
    global _lowrow_flag

    with open(_input_template_fpath, 'r') as fp:
        out_text = fp.read()

    for idx, class_name in enumerate(data):

        if idx > 0:
            # at each new class, flip the row type flag back to previous row, then flip again for next row
            _lowrow_flag = not _lowrow_flag
            out_text += f'<tr class=row{get_row_type()}>\n<td colspan=31><a name="{class_name}"></a><HR></td>\n</tr>\n'
            _lowrow_flag = not _lowrow_flag

        for driver_name in data[class_name]:
            num = int(driver_name.split()[-1])
            cls = f'hardo{_pax_classes[num%len(_pax_classes)]}' if 'hardo' in class_name else class_name

            out_text += f'<tr class=row{get_row_type()}>\n'
            out_text += f'<td nowrap align="right">{cls:s}</td>\n'
            out_text += f'<td nowrap align="right">{num:d}</td>\n'
            out_text += f'<td nowrap align="left">{driver_name:s}</td>\n'

            for run in data[class_name][driver_name]:
                run_txt = format_run(run)
                out_text += f'<td valign="top" nowrap >{run_txt:s}</td>\n'
            out_text += f'</tr>\n'

            # flip row type flag after each driver
            _lowrow_flag = not _lowrow_flag

    # terminate file
    out_text += '</tbody></table>\n\n'
    out_text += '</BODY>\n'
    out_text += '</HTML>\n'

    with open(_output_fpath, 'w') as fp:
        fp.write(out_text)
        fp.flush()

# generate data dict (data[class][driver_name] --> list of {time:float, cones:int, dnf:bool} dicts
data = {}
for d in range(1, _num_drivers+1):
    c = random.choice(_classes)
    if c not in data:
        data[c] = {}

    data[c][f'Driver {d:03d}'] = [None]*_num_runs

# clear data file
generate_htm(data)

# main loop
total_run_count = 1
for run_num in range(1, _num_runs + 1):

    for c in data:
        for d in data[c]:
            runs = data[c][d]

            new_run = {
                'time': random.uniform(_min_run_time, _max_run_time),
                'cones': floor(random.paretovariate(2) - 1),
                'dnf': random.paretovariate(5) > 2.0
            }

            print(f'Adding result {total_run_count:04d}: {d:s} [{c:s}/{run_num:d}]: {format_run(new_run):s}')

            # create new run
            runs[run_num-1] = new_run

            # generate htm output
            generate_htm(data)

            # sleep
            sleep(_refresh_rate_sec)

            total_run_count += 1