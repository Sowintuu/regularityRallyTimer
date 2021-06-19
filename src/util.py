from math import floor


def decode_seconds(time_seconds):
    time_decoded = [0.0] * 4
    # Hours.
    time_decoded[0] = floor(time_seconds / 3600)

    # Minutes.
    time_decoded[1] = floor((time_seconds - time_decoded[0] * 3600) / 60)

    # Seconds.
    seconds_float = time_seconds - time_decoded[0] * 3600 - time_decoded[1] * 60
    time_decoded[2] = floor(seconds_float)

    # Thousandths.
    time_decoded[3] = floor((seconds_float - floor(seconds_float)) * 1000)

    return time_decoded
