<p align="center"><img src="./_readme/Diagram.drawio.png" /></p>

Server
```bash
uv run python src/server.py
```

API Example
```
GET http://127.0.0.1:8888/get?url=<url>
```

Test with Client
```bash
uv run python -m http.server --directory data
uv run python src/client.py
```
