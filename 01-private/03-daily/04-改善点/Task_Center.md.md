---
cssclass: task-dashboard
---

# Task Center

---

## プロジェクト別ビュー

### AirCle
```dataview
task
where !completed and contains(tags, "@aircle")
sort due asc
```

### ClimbBeyond
```dataview
task
where !completed and contains(tags, "@climbbeyond")
sort due asc
```

### Genspark
```dataview
task
where !completed and contains(tags, "@genspark")
sort due asc
```

### VideoPocket
```dataview
task
where !completed and contains(tags, "@videopocket")
sort due asc
```

---

## 完了タスク（過去30件）
```dataview
task
where completed
sort completed desc
limit 30
```
