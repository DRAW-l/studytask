-- StudyTask 建表脚本：与《设计说明书》附录 A 保持一致
CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT    NOT NULL,
    course      TEXT    NOT NULL,
    description TEXT    NOT NULL DEFAULT '',
    due_date    TEXT    NOT NULL,
    priority    TEXT    NOT NULL DEFAULT '中',
    status      TEXT    NOT NULL DEFAULT '待完成',
    created_at  TEXT    NOT NULL,
    updated_at  TEXT    NOT NULL,
    CONSTRAINT ck_title_len   CHECK (length(title) BETWEEN 1 AND 100),
    CONSTRAINT ck_course_len  CHECK (length(course) BETWEEN 1 AND 60),
    CONSTRAINT ck_desc_len    CHECK (length(description) <= 1000),
    CONSTRAINT ck_due_format  CHECK (due_date GLOB
        '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),
    CONSTRAINT ck_priority    CHECK (priority IN ('高', '中', '低')),
    CONSTRAINT ck_status      CHECK (status IN ('待完成', '进行中', '已完成'))
);

CREATE INDEX IF NOT EXISTS idx_tasks_due      ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_course   ON tasks(course);
CREATE INDEX IF NOT EXISTS idx_tasks_status   ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
