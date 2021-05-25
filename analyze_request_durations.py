#!/usr/bin/env python

from __future__ import print_function

import argparse
import json
import os

# This value was emirically determined on an iMac Pro with a fairly small sample size.
# All measurements in seconds should be taken with extreme care
INSTRUCTIONS_PER_SECOND = 6693088549.09358

# The length of the bars in the histograms
HISTOGRAM_BAR_LENGTH = 40


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('request_durations_file')
    return parser.parse_args()


def print_stats(entries):
    """
    entries is a list of dictionaries from the JSON file under the
    files.<file-name>.<request-name> path containing the following keys
    - totalInstructions
    - logHistogram
    - requestsExecuted
    """

    # Create a log histogram for all entries
    aggregated_completion_log_histogram = {}
    # Adds totalInstruction for each entry
    total_instructions = 0
    # Adds requestsExecuted for each entry
    total_requests_executed = 0
    for entry in entries:
        total_instructions += int(entry['totalInstructions'])
        total_requests_executed += int(entry['requestsExecuted'])
        for (bucket, count) in entry['logHistogram'].iteritems():
            bucket = int(bucket)
            count = int(count)
            if bucket not in aggregated_completion_log_histogram:
                aggregated_completion_log_histogram[bucket] = 0
            aggregated_completion_log_histogram[bucket] += count

    if total_requests_executed == 0:
        print('No requests executed')
        return

    print('Requests: {}'.format(total_requests_executed))

    average_instructions_per_request = total_instructions / total_requests_executed
    seconds_estimate = average_instructions_per_request / INSTRUCTIONS_PER_SECOND
    print('Average: {:.0e} instr (ca. {:.3f}s)'
          .format(average_instructions_per_request, seconds_estimate))

    print('\nHistogram:')

    min_bucket = min(aggregated_completion_log_histogram)
    max_bucket = max(aggregated_completion_log_histogram)
    max_count = max([x[1] for x in aggregated_completion_log_histogram.iteritems()])

    # Sums up the percentages for each entry to make it easier to spot the
    # n-th percentile in the histogram
    running_percentage_sum = 0
    for bucket in range(min_bucket, max_bucket + 1):
        count = aggregated_completion_log_histogram.get(bucket, 0)
        executed_instructions = pow(2, bucket)
        estimated_seconds = executed_instructions / INSTRUCTIONS_PER_SECOND
        bar_fill = (count * HISTOGRAM_BAR_LENGTH / max_count)
        bar = '*' * bar_fill + ' ' * (HISTOGRAM_BAR_LENGTH - bar_fill)
        percentage = float(count) / total_requests_executed * 100
        running_percentage_sum += percentage
        print('< {:5.0e} instr (ca. {:6.3f}s): {} {:4.1f}% (< {:5.1f}%)'
              .format(executed_instructions, estimated_seconds, bar, percentage,
                      running_percentage_sum))


def print_stats_for_all_files(request_durations, request_name):
    print('\n---------- All {} requests ----------\n'.format(request_name))
    all_request_entries = []
    for (file_name, file_stats) in request_durations['files'].iteritems():
        all_request_entries.append(file_stats[request_name])
    print_stats(all_request_entries)


def print_slowest_files(request_durations, request_name, num_files):
    print('\n---------- {} slowest files for {} requests ----------\n'
          .format(num_files, request_name))

    file_and_average = []
    for (file_name, file_stats) in request_durations['files'].iteritems():
        instr_executed_in_file = int(file_stats[request_name]['totalInstructions'])
        requests_in_file = int(file_stats[request_name]['requestsExecuted'])
        if requests_in_file > 0:
            average = instr_executed_in_file / requests_in_file
            file_and_average.append((file_name, average))
    file_and_average = sorted(file_and_average, key=lambda x: x[1], reverse=True)

    for (file_name, average_request_duration) in file_and_average[0:num_files]:
        print('-- {} --\n'.format(file_name))
        print_stats([request_durations['files'][file_name][request_name]])
        print('\n')


def print_seconds_disclaimer():
    print('''IMPORTANT:
All measurements printed by this script were done in number of number of
instructions. Measurements in seconds are computed assuming that all machines
execute the same number of instructions per second at all times, which is not
correct. Thus all measurements in seconds should be taken with extreme care.
As they scale linearly with the number of instructions, it is safe to compare
values in seconds output by this script.
''')


def analyze_request_durations(file):
    if not os.path.exists(file):
        print('{} does not exist. No request durations to analyze.'.format(file))
        return
    print_seconds_disclaimer()
    print('\n---------- Raw durations for further analysis ----------\n')
    with open(file, 'r') as json_file:
        print(json_file.read())

    with open(file, 'r') as json_file:
        request_durations = json.load(json_file, encoding='utf-8')
    print_stats_for_all_files(request_durations, 'CodeComplete')
    print_slowest_files(request_durations, 'CodeComplete', 10)


def main():
    args = parse_args()
    analyze_request_durations(args.request_durations_file)


if __name__ == '__main__':
    main()
