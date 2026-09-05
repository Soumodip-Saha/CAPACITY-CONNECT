import sys, os
sys.path.insert(0, os.path.abspath('.'))
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
resp = client.get('/auth/demo-login/trainer', follow_redirects=False)
client.cookies.set('capacity_connect_session', resp.cookies.get('capacity_connect_session'))
r = client.get('/trainer/courses')
print('Status:', r.status_code)
import re
titles = re.findall(r'<h3[^>]*>(.*?)</h3>', r.text)
for t in titles:
    print('Found H3:', t.strip())
