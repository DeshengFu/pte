# What is PTE

PTE (Python Test Engine) is a lightweight test engine designed for easy functional testing (e.g., testing REST interfaces) by anyone.

# Getting Started

## Installation

No special installation steps are required. Simply install the latest version of Python 3 and all modules listed in the `requirements.txt` file. Configure your `venv` as needed, and you're ready to go.

An example test system with several test suites is defined under the `tests` folder. You can use `python3 run.py -tp tests` to run the example tests. It's normal for some tests to fail.

You’ll see console output like the following:

```
...

2025-05-30 12:06:04 [info     ] ======================================================
2025-05-30 12:06:04 [info     ] [START] Test: Initialize Step 1 (1 / 1 tests).
2025-05-30 12:06:04 [info     ] Executing script (config.json: initCmd)
2025-05-30 12:06:09 [info     ] Script is executed (config.json: initCmd).
2025-05-30 12:06:09 [info     ] [OKAY ] Test: Initialize Step 1 (1 / 1 tests).
2025-05-30 12:06:09 [info     ] ======================================================
2025-05-30 12:06:09 [info     ] [OKAY ] Test suite: Initialize (1 tests).
2025-05-30 12:06:09 [info     ] ======================================================
2025-05-30 12:06:09 [info     ]                               
2025-05-30 12:06:09 [info     ]                               
2025-05-30 12:06:09 [info     ] ======================================================
2025-05-30 12:06:09 [info     ] [START] Test: JSON Test (1 / 1 tests).

...

2025-05-30 12:06:09 [error    ] ======================================================
2025-05-30 12:06:09 [error    ] [ERROR] Test suite: Rest Test Suite (1 tests).
2025-05-30 12:06:09 [error    ] ======================================================
2025-05-30 12:06:09 [error    ]                               
2025-05-30 12:06:09 [info     ]                               
2025-05-30 12:06:09 [info     ] ======================================================
2025-05-30 12:06:09 [info     ] [START] Test: Hello World Test (1 / 1 tests).
2025-05-30 12:06:09 [info     ]   * Say "Hello World" and return okay
2025-05-30 12:06:09 [info     ] [OKAY ] Test: Hello World Test (1 / 1 tests).
2025-05-30 12:06:09 [info     ] ======================================================
2025-05-30 12:06:09 [info     ] [OKAY ] Test suite: Basic Test Suite (1 tests).
2025-05-30 12:06:09 [info     ] ======================================================
2025-05-30 12:06:09 [info     ]                               
2025-05-30 12:06:09 [info     ]                               
2025-05-30 12:06:09 [info     ] ======================================================
2025-05-30 12:06:09 [info     ] [START] Test: Uninitialize Step 1 (1 / 1 tests).
2025-05-30 12:06:09 [info     ] Executing script (config.json: uninitCmd)
```

## Understand the Arguments

You can start your tests using `run.py` as shown in the previous example. You can also integrate PTE into your own system by calling the `run` function from the `pte` module manually. In either case, you need to understand the available arguments to customize your run.

| Name        | Argument       | Short | Value Type     | Description |
|-------------|----------------|-------|----------------|-------------|
| test path   | --test-path    | -tp   | path to folder | The root path of your test system. |
| run path    | --run-path     | -rp   | path to folder | A subpath of the test path. Only tests in this path will be executed. If unspecified, the test path is also used as the run path. |
| state file  | --state-file   | -s    | path to file   | Stores the state of the current run. PTE periodically updates this file. Other tools (e.g., Jenkins) can read it to check progress. |
| dry run     | --dry-run      | -d    | none (boolean) | If specified, performs a dry run instead of actual execution. Useful to preview which tests will be executed. |
| no scan     | --no-scan      | -ns   | none (boolean) | If specified, no scan run is performed. A scan run is similar to a dry run but also collects metadata (e.g., total number of test suites). Recommended to skip scan for dry runs. |

## Understand Test, Test Suite, and Test System

- A **test** is a function that returns `True` (success) or `False` (failure). It can also log details to the console.

- A **test suite** is a collection of one or more related tests, defined in a single Python script. A test suite is considered successful only if all its tests pass.

- A **test system** is a folder tree that can include subfolders of arbitrary depth. All `.py` files not starting with an underscore (`_`) are treated as test suites—except for special cases described below. PTE traverses this tree in a depth-first manner and runs the test suites sequentially.

In each folder, you can define `_initialize.py` and/or `_uninitialize.py`. These are special test suites for initialization and cleanup. During execution:

1. PTE executes `_initialize.py` if it exists.
2. Then it runs the regular test suites and traverses subfolders.
3. Finally, it executes `_uninitialize.py` if it exists.

This setup allows you to build a structured hierarchy of initialization and cleanup logic.

If you need to initialize the system from the top level but don’t want to execute all test suites, you can specify a different **run path**. The initialization and uninitialization still start from the **test path**, but only regular test suites in the **run path** are executed.

## Write Your Test and Test Suite

A basic test suite looks like this:

```python
import pte

class TestSuite(pte.PteTestSuite):
    def __init__(self):
        super().__init__("Basic Test Suite")
testSuite = TestSuite()
def run():
    testSuite.run()

class Test1(pte.PteTest):
    def __init__(self):
        super().__init__(testSuite, "Hello World Test")

    def execute(self):
        pte.logger.info("  * Say \"Hello World\" and return okay")
        return True
Test1()
```

First, define the test suite and create its instance. Then define and instantiate the test classes. You can skip a test or suite by passing a boolean value:

```python
super().__init__("Basic Test Suite", False)
```

```python
super().__init__(testSuite, "Hello World Test", False)
```

When a test suite is skipped, all tests within it are skipped as well, regardless of their individual skip settings.

## Built-in Helper for Executing System Commands

PTE includes a helper for executing system commands, often useful for initialization and cleanup. Here’s an example from `tests/mytest/_initialize.py`:

```python
import pte
import pterest
import ptescript

...

    def execute(self):
        ptescript.run("config.json", "initCmd")
        return True

...
```

This loads the command list from the `initCmd` field in `config.json` and executes them sequentially. Example:

```json
"initCmd": [
    ["sleep", "5"]
],
```

> You may need `sudo` or special permissions to execute certain commands.

## Built-in REST Test

PTE provides a built-in test class to simplify testing REST interfaces. Example:

```python
import pte
import pterest

...

test2 = pterest.PteRestJsonTest(testSuite, "JSON Test", url="http://localhost/", method="get", expJSON={"result": "Hello World"})

...
```

Available classes:

- `PteRestBasicTest`: tests raw string responses.
- `PteRestJsonTest`: tests JSON responses. Ignores formatting and key order differences.
- `PteRestBasicFileTest`: compares raw string responses with content in an external file.
- `PteRestJsonFileTest`: compares JSON responses with content in an external file.

For more details, refer to `pterest.py`.

# License

This package is licensed under the MIT License.
