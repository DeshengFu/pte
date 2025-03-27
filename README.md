What is PTE
=====

PTE (Python Test Engine) is a lightweight test engine. It's aimed for functional test (e.g. test of REST interfaces).

Getting Started
====

You can just run the <code>run.py</code> to run the example tests defined unter <code>tests</code>.

For example, the following line will check the localhost root and verify if the result JSON file is equal to the expected value (expJSON).

```
test1 = pterest.PteRestJsonTest(testSuite, "JSON Test", url="http://localhost/", method="get", expJSON={"result": "Hello World"})
```

If the REST interface is okay, you will get a response like this:
```
2025-03-27 19:25:23 [info     ] [START] Test: Hello World Test (1 / 1 tests).
2025-03-27 19:25:23 [info     ]   * Say "Hello World" and return okay
2025-03-27 19:25:23 [info     ] [OKAY ] Test: Hello World Test (1 / 1 tests).
2025-03-27 19:25:23 [info     ] [OKAY ] Test suite: Basic Test Suite (1 tests).
2025-03-27 19:25:23 [info     ] [START] Test: JSON Test (1 / 1 tests).
2025-03-27 19:25:23 [info     ] [OKAY ] Test: JSON Test (1 / 1 tests).
2025-03-27 19:25:23 [info     ] [OKAY ] Test suite: Rest Test Suite (1 tests).
```

License
===
The package is licensed under MIT.