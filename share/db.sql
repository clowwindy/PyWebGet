

PRAGMA foreign_keys = OFF;

-- ----------------------------
-- Table structure for "main"."Task"
-- ----------------------------
DROP TABLE "main"."Task";
CREATE TABLE "Task" (
"id"  INTEGER,
"url"  TEXT NOT NULL,
"status"  INTEGER NOT NULL DEFAULT 0,
"filename"  TEXT,
"partfilename"  TEXT,
"dir"  TEXT,
"cookie"  TEXT,
"referer"  TEXT,
"priority"  INTEGER NOT NULL DEFAULT 0,
"completed_size"  INTEGER NOT NULL DEFAULT 0,
"total_size"  INTEGER NOT NULL DEFAULT 0,
"date_created"  INTEGER NOT NULL DEFAULT 0,
"date_completed"  INTEGER NOT NULL DEFAULT 0,
PRIMARY KEY ("id" ASC)
);

-- ----------------------------
-- Records of Task
-- ----------------------------
