from interpret import getBashOutput

try:
	import apiclient
except ImportError:
    getBashOutput("pip install --upgrade google-api-python-client")
