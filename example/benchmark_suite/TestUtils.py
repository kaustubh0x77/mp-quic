from datetime import datetime
import os
import subprocess
from shutil import move as mv
from pprint import pprint
import json
from copy import deepcopy

from setup_experiment import setup_experiment
from BwmParser import BwmParser

class TestUtils:

    BWMNG_OUTPUT_FILE = '/tmp/bwmng_result.csv'

    @staticmethod
    def start_network(experiment_id):
        net = setup_experiment(experiment_id)
        client = net.getNodeByName('client')
        server = net.getNodeByName('server')
        return (net, client, server)

    @staticmethod
    def run_tcp_server(host):
        print('Starting TCP server...',end='')
        host.popen('python3 tcp_server.py')
        print('DONE!')

    @staticmethod
    def run_tcp_client(host):
        print('Now running TCP client...')
        return int(host.cmd('python3 tcp_client.py'))

    @staticmethod
    def run_mpquic_server(host):
        print('Starting MPQUIC server...',end='')
        host.popen('go run mpquic_server.go')
        print('DONE!')

    @staticmethod
    def run_mpquic_client(host):
        print('Now running MPQUIC client...')
        return int(host.cmd('go run mpquic_client.go'))

    @staticmethod
    def run_quic_client(host):
        print('Now running QUIC client...')
        return int(host.cmd('go run quic_client.go'))

    @staticmethod
    def generate_results_dir(experiment_id):
        test_id = '_'.join([
            experiment_id, str(int(datetime.now().timestamp()))])
        results_dir = os.path.join(os.getcwd(), 'results', test_id)
        if os.path.exists(results_dir):
            raise FileExistsError('Test already exists')
        else:
            os.makedirs(results_dir)
        return results_dir

    @staticmethod
    def run_bwmng():
        print('Starting bwm-ng...',end='')
        process = subprocess.Popen(
            ['exec ./bwm-ng.sh {}'.format(TestUtils.BWMNG_OUTPUT_FILE)],shell=True)
        print('DONE!')
        return process

    @staticmethod
    def generate_report(time_taken, goodput, throughtputs, iterations, data_sent, subtest_dir, transfers):
        report = {
            'Data block size (in bytes)': data_sent,
            'Number of iterations': iterations,
            'Total data transferred (MBytes)': data_sent / iterations / (1024 * 1024),
            'Total time taken (s)': time_taken,
            'Goodput (MBytes/s)': goodput,
            'Transfers (Bytes)': transfers,
            'Throughputs: (MBytes/s)': throughtputs,
        }

        print('\nREPORT:')
        print(json.dumps(report,indent=4))

        report_file = os.path.join(subtest_dir, 'report.json')
        with open(report_file, 'w+') as f:
            json.dump(report, f, indent=4)
            f.close()

    @staticmethod
    def dump_result(
        results_base_dir,
        subtest_name,
        time_taken,
        data_sent,
        iterations,
        ):

        subtest_dir = os.path.join(results_base_dir, subtest_name)
        os.mkdir(subtest_dir)
        bwmng_results_file = os.path.join(subtest_dir,'bwmng_results.csv')
        mv(TestUtils.BWMNG_OUTPUT_FILE, bwmng_results_file)

        time_taken = time_taken / 1000000000 # Seconds
        goodput = 1.0*(data_sent)*(iterations) / time_taken/1024/1024 # MBytes/s

        bwm_parser = BwmParser(bwmng_results_file)

        throughputs = deepcopy(bwm_parser.transfers)
        print(throughputs)

        for direction, thruput in throughputs.items():
            for iface, val in thruput.items():
                throughputs[direction][iface] = val / time_taken / (1024 * 1024)

        TestUtils.generate_report(
            time_taken, goodput, throughputs, 
            iterations, data_sent, subtest_dir,
            bwm_parser.transfers
        )