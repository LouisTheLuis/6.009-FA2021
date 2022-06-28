#!/usr/bin/env python3
import os
import sys
import copy
import json
import pickle

import lab

sys.setrecursionlimit(10000)

import pytest

TEST_DIRECTORY = os.path.dirname(__file__)


def flip_board(game):
    return [[game[x][y] for x in range(len(game))] for y in range(len(game[0]))]


flip_direction = {
    "up": "left",
    "left": "up",
    "down": "right",
    "right": "down",
}


def compare_boards(your_board, expected_board, step_num):
    assert len(your_board) == len(
        expected_board
    ), f"board had wrong size on step {step_num}"
    for rn, (your_row, expected_row) in enumerate(zip(your_board, expected_board)):
        assert len(your_row) == len(
            expected_row
        ), f"row {rn} had wrong size on step {step_num}"
        for cn, (your_cell, expected_cell) in enumerate(zip(your_row, expected_row)):
            assert sorted(your_cell) == sorted(
                expected_cell
            ), f"objects at location ({rn},{cn}) don't match on step {step_num}"


def compare_simulation(filename):
    with open(os.path.join(TEST_DIRECTORY, "test_levels", f"{filename}.json")) as f:
        level = json.load(f)
    with open(os.path.join(TEST_DIRECTORY, "test_inputs", f"{filename}.txt")) as f:
        inputs = f.read().strip().splitlines(False)
    with open(os.path.join(TEST_DIRECTORY, "test_outputs", f"{filename}.json")) as f:
        outputs = json.load(f)
    assert len(inputs) == len(outputs) != 0

    game = lab.new_game(copy.deepcopy(level))
    compare_boards(lab.dump_game(game), level, 0)
    for ix, (direction, (exp_dump, exp_win)) in enumerate(zip(inputs, outputs)):
        victory = lab.step_game(game, direction)
        assert victory == exp_win
        compare_boards(lab.dump_game(game), exp_dump, ix + 1)

    # trip to flip x,y for everything
    level2 = flip_board(level)
    game = lab.new_game(copy.deepcopy(level2))
    compare_boards(lab.dump_game(game), level2, 0)
    for ix, (direction, (exp_dump, exp_win)) in enumerate(zip(inputs, outputs)):
        victory = lab.step_game(game, flip_direction[direction])
        assert victory == exp_win
        compare_boards(lab.dump_game(game), flip_board(exp_dump), ix + 1)


test_cases = [
    i.rsplit(".", 1)[0]
    for i in sorted(os.listdir(os.path.join(TEST_DIRECTORY, "test_levels")))
]


@pytest.mark.parametrize("sim", test_cases)
def test_simulation(sim):
    compare_simulation(sim)


if __name__ == "__main__":
    import os
    import sys
    import json
    import pickle
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--gather", action="store_true")
    parser.add_argument("--server", action="store_true")
    parser.add_argument("--initial", action="store_true")
    parser.add_argument("args", nargs="*")

    parsed = parser.parse_args()

    class TestData:
        def __init__(self, gather=False):
            self.alltests = None
            self.results = {"passed": []}
            self.gather = gather

        @pytest.hookimpl(hookwrapper=True)
        def pytest_runtestloop(self, session):
            yield

        def pytest_runtest_logreport(self, report):
            if report.when != "call":
                return
            self.results.setdefault(report.outcome, []).append(report.head_line)

        def pytest_collection_finish(self, session):
            if self.gather:
                self.alltests = [i.name for i in session.items]

    pytest_args = ["-v", __file__]

    if parsed.server:
        pytest_args.insert(0, "--color=yes")

    if parsed.gather:
        pytest_args.insert(0, "--collect-only")

    testinfo = TestData(parsed.gather)
    res = pytest.main(
        ["-k", " or ".join(parsed.args), *pytest_args], **{"plugins": [testinfo]}
    )

    if parsed.server:
        _dir = os.path.dirname(__file__)
        if parsed.gather:
            with open(
                os.path.join(_dir, "alltests.json"), "w" if parsed.initial else "a"
            ) as f:
                f.write(json.dumps(testinfo.alltests))
                f.write("\n")
        else:
            with open(
                os.path.join(_dir, "results.json"), "w" if parsed.initial else "a"
            ) as f:
                f.write(json.dumps(testinfo.results))
                f.write("\n")
