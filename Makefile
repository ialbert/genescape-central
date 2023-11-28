#
# Need the hatch tool to run this Makefile.
#
# pipx install hatch
#

# Usage information.
usage:
	@echo "#"
	@echo "# Use the source, Luke!"
	@echo "#"

# Performs the testing.
test:
	hatch run test

# Runs a linter.
lint:
	hatch run lint:all
	hatch run lint:typing

# Fix linting errors.
fix:
	hatch run lint:fmt

dist:
	hatch build 

pypi:
	hatch run publish


