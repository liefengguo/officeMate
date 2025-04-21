# 示例用法
from core.snapshot import SnapshotManager

sm = SnapshotManager()
info = sm.create_snapshot("/Users/guoliefeng/tjut/大论文参考/研究生学位论文修改说明.docx")
print(info)
