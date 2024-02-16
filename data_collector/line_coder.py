import ap_dict
import os


# このファイルがあるdirと同一dirにある'収集路線'と言うファイルを読み込む
path = os.path.join(os.path.dirname(__file__), '収集路線')
with open(path, 'r') as f:
    while True:
        line = f.readline()
        if "—" in line:
            from_ap = line.split("—")[0]
            to_ap = line.split("—")[1].strip()
            try:
                output = "".join([ap_dict.encode(from_ap), "-", ap_dict.encode(to_ap)])
            except TypeError:
                print(from_ap, to_ap)
            print(output)
        if not line:
            break
