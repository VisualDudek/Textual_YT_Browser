[group("Meta")]
[doc("List available recipes")]
_default:
	@just --list

[group("Start App")]
[doc("Start the Textual app")]
app:
	uv run main
