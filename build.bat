bumpver update --patch
python -m build
twine upload -r pypi dist/*
