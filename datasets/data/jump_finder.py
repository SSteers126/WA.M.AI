# Finds if any labels jump backwards in frames, or if the same frame is labelled multiple times in a row.
# (This is extremely crude, it's been thrown together to fix a mess I made)

with open("TEST-okinimesumama-expert-24-played-incomplete/labels.csv") as f:
    frame_num = -1
    last_frame_num = -1
    total_errors = 0
    for line in f.readlines():
        try:
            last_frame_num = frame_num
            frame_num = int(line.split(".")[0].split("-")[-1])
            if frame_num <= last_frame_num or abs(frame_num - last_frame_num) > 1:
                print(frame_num, last_frame_num)
                total_errors += 1


        except:
            pass
    print(total_errors)