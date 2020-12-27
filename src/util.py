from math import floor


def decode_seconds(time_seconds):
    time_decoded = [0.0] * 3
    time_decoded[0] = floor(time_seconds / 3600)
    time_decoded[1] = floor((time_seconds - time_decoded[0] * 3600) / 60)
    time_decoded[2] = time_seconds - time_decoded[0] * 3600 - time_decoded[1] * 60

    return time_decoded
