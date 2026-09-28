"""Exercise all public pages against the frozen 100-firm snapshot."""
from pathlib import Path
import sys
from streamlit.testing.v1 import AppTest

sys.stdout.reconfigure(encoding='utf-8')
root=Path(__file__).resolve().parents[1]
entrypoint = root / 'app.py' if (root / 'app.py').exists() else root / 'streamlit_deploy' / 'app.py'
app=AppTest.from_file(str(entrypoint),default_timeout=90).run()
assert not app.exception,app.exception
for page in ('Tổng quan','Khám phá báo cáo','Kiểm định mô hình','Phương pháp & audit','Báo cáo & tài liệu'):
    app.sidebar.radio[0].set_value(page).run()
    assert not app.exception,(page,app.exception)
    print('OK',page)
