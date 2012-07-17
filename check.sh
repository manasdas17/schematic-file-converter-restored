#!/bin/sh

echo "Running the linter..."
scons lint

if [ ! $? -eq 0 ]; then
	echo "Error: Linter failed (scons lint)."
	echo
	echo "The linter finds stylistic inconsistencies"
	echo "which make the project harder to understand,"
	echo "fork and modify."
	echo
	echo "Please run the linter and resolve any issues"
	echo "it finds using:"
	echo
	echo "  scons lint"
	echo
	exit 1
else
    echo "Success: Linter passed (scons lint)."
fi


echo "Running the unit tests..."
scons test

if [ ! $? -eq 0 ]; then
	echo "Error: Unit tests failed (scons test)."
	echo
	echo "The unit tests find errors in specification"
	echo "implementation and are normally the result"
	echo "of partial changes to the spec or improper"
	echo "implementation."
	echo
	echo "Please run the tests and resolve any issues"
	echo "it finds using:"
	echo
	echo "  scons test"
	echo
	exit 1
else
    echo "Success: Unit tests passed (scons test)."
fi


echo "Running the regression tests..."
python test/test.py

if [ ! $? -eq 0 ]; then
	echo "Error: Regression tests failed (python test/test.py)."
	echo
	echo "The regression tests find errors and failures"
	echo "through the processing of a large set of"
	echo "real-world design files."
	echo
	echo "Please run the tests and resolve any issues"
	echo "it finds using:"
	echo
	echo "  python test/test.py"
	echo
	exit 1
else
    echo "Success: Regression tests passed (python test/test.py)."
fi
