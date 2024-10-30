# Desmos Drive
*Note: Not affiliated with Desmos*
### Using this tool to upload large amounts of data violates Desmos’s terms of service and may jeopardize your ability to continue to use Desmos’s tools.
## Features
- Store ~~small~~ **any** files on Desmos servers
- No API key required
- No security :D
## Usage
- Install dependencies: `pip install -r requirements.txt`
- Run `python3 DesmosDrive.py`
- If uploading, move desired file into the same directory before selecting
- When downloading, file will download to the same directory
## How does it work?
When saving a graph on Desmos, your browser sends an HTTP Request to the server - which includes (among other information) the graph's hash (url id) and the graph's thumbnail (encoded with base64). This program mimics those requests, but uses its own randomly generated hashes and generated thumbnails.

When uploading a file, it is first converted to binary. Then, the binary is converted into sequential R,G, and B values, which are converted to an image. If the file is too large for one Desmos thumbnail, it is split into smaller chunks and individually uploaded. The hash of each thumbnail is stored for later reference when downloading, which reverses the process to recover the original file.

### Example:
1. File: `test.txt`->`hello world`
2. Binary: `01101000 01100101 01101100...`
3. RGB: `(104,101,108)...`
4. RGB Pixels -> PNG -> Upload!

#### "Why not just upload the binary as equations in the Desmos graph?"
- Where's the fun in that?
