-- SQLite schema for sino database

-- Table: sino_ad
CREATE TABLE IF NOT EXISTS sino_ad (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    typeid INTEGER NOT NULL,
    subject TEXT NOT NULL,
    content TEXT NOT NULL,
    status INTEGER NOT NULL DEFAULT 0,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL
);

-- Table: sino_admin
CREATE TABLE IF NOT EXISTS sino_admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    typer TEXT NOT NULL DEFAULT 'editor',
    user TEXT NOT NULL DEFAULT '',
    pass TEXT NOT NULL DEFAULT '',
    email TEXT NOT NULL DEFAULT '',
    modulelist TEXT NOT NULL
);

-- Table: sino_book
CREATE TABLE IF NOT EXISTS sino_book (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    typeid INTEGER NOT NULL DEFAULT 0,
    userid INTEGER NOT NULL DEFAULT 0,
    user TEXT NOT NULL DEFAULT '',
    subject TEXT NOT NULL DEFAULT '',
    content TEXT NOT NULL,
    postdate INTEGER NOT NULL DEFAULT 0,
    email TEXT NOT NULL DEFAULT '',
    ifcheck INTEGER NOT NULL DEFAULT 0,
    language INTEGER NOT NULL DEFAULT 0,
    reply TEXT NOT NULL,
    replydate INTEGER NOT NULL DEFAULT 0
);

-- Table: sino_category
CREATE TABLE IF NOT EXISTS sino_category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sysgroupid INTEGER NOT NULL DEFAULT 0,
    rootid INTEGER NOT NULL DEFAULT 0,
    parentid INTEGER NOT NULL DEFAULT 0,
    catename TEXT NOT NULL DEFAULT '',
    catestyle TEXT NOT NULL DEFAULT '',
    taxis INTEGER NOT NULL DEFAULT 255,
    tpl_index TEXT NOT NULL DEFAULT '',
    tpl_list TEXT NOT NULL DEFAULT '',
    tpl_msg TEXT NOT NULL DEFAULT '',
    note TEXT NOT NULL DEFAULT '',
    status INTEGER NOT NULL DEFAULT 1,
    language INTEGER NOT NULL DEFAULT 0,
    psize INTEGER NOT NULL DEFAULT 30,
    isrefreshcount INTEGER NOT NULL DEFAULT 1,
    msgcount INTEGER NOT NULL DEFAULT 0,
    showtype INTEGER NOT NULL DEFAULT 0
);

-- Table: sino_feedback
CREATE TABLE IF NOT EXISTS sino_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userid INTEGER NOT NULL DEFAULT 0,
    subject TEXT NOT NULL DEFAULT '',
    content TEXT NOT NULL,
    postdate INTEGER NOT NULL DEFAULT 0,
    reply TEXT NOT NULL,
    replydate INTEGER NOT NULL DEFAULT 0
);

-- Table: sino_job
CREATE TABLE IF NOT EXISTS sino_job (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jobname TEXT NOT NULL DEFAULT '',
    usercount INTEGER NOT NULL DEFAULT 0,
    age TEXT NOT NULL DEFAULT '',
    experience TEXT NOT NULL DEFAULT '',
    height TEXT NOT NULL DEFAULT '',
    gender INTEGER NOT NULL DEFAULT 0,
    content TEXT NOT NULL,
    postdate INTEGER NOT NULL DEFAULT 0,
    enddate INTEGER NOT NULL DEFAULT 0,
    language INTEGER NOT NULL DEFAULT 0
);

-- Table: sino_jobapp
CREATE TABLE IF NOT EXISTS sino_jobapp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jobid INTEGER NOT NULL DEFAULT 0,
    userid INTEGER NOT NULL DEFAULT 0,
    jobname TEXT NOT NULL DEFAULT '',
    name TEXT NOT NULL DEFAULT '',
    age INTEGER NOT NULL DEFAULT 0,
    height INTEGER NOT NULL DEFAULT 150,
    schoolage TEXT NOT NULL DEFAULT '',
    contact TEXT NOT NULL DEFAULT '',
    photo TEXT NOT NULL DEFAULT '',
    note TEXT NOT NULL,
    postdate INTEGER NOT NULL DEFAULT 0
);

-- Table: sino_lang
CREATE TABLE IF NOT EXISTS sino_lang (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sign TEXT NOT NULL DEFAULT '',
    name TEXT NOT NULL DEFAULT '',
    ifuse INTEGER NOT NULL DEFAULT 0,
    ifdefault INTEGER NOT NULL DEFAULT 0,
    ifsystem INTEGER NOT NULL DEFAULT 0,
    template INTEGER NOT NULL DEFAULT 0,
    langc TEXT NOT NULL
);

-- Table: sino_link
CREATE TABLE IF NOT EXISTS sino_link (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL DEFAULT '',
    url TEXT NOT NULL DEFAULT '',
    picture TEXT,
    taxis INTEGER DEFAULT 255
);

-- Table: sino_mailmsg
CREATE TABLE IF NOT EXISTS sino_mailmsg (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    language INTEGER NOT NULL DEFAULT 0,
    subject TEXT NOT NULL DEFAULT '',
    content TEXT NOT NULL,
    usetype TEXT NOT NULL DEFAULT ''
);

-- Table: sino_mailstatus
CREATE TABLE IF NOT EXISTS sino_mailstatus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    status INTEGER NOT NULL DEFAULT 0,
    sign TEXT NOT NULL DEFAULT '',
    language INTEGER NOT NULL DEFAULT 1
);

-- Table: sino_msg
CREATE TABLE IF NOT EXISTS sino_msg (
    id INTEGER NOT NULL,
    cateid INTEGER NOT NULL DEFAULT 0,
    subject TEXT NOT NULL DEFAULT '',
    style TEXT NOT NULL DEFAULT '',
    author TEXT NOT NULL DEFAULT '',
    authorid INTEGER NOT NULL DEFAULT 0,
    postdate INTEGER NOT NULL DEFAULT 0,
    modifydate INTEGER NOT NULL DEFAULT 0,
    thumb INTEGER NOT NULL DEFAULT 0,
    tplfile TEXT NOT NULL DEFAULT '',
    hits INTEGER NOT NULL DEFAULT 0,
    orderdate INTEGER NOT NULL DEFAULT 0,
    istop INTEGER NOT NULL DEFAULT 0,
    isvouch INTEGER NOT NULL DEFAULT 0,
    isbest INTEGER NOT NULL DEFAULT 0,
    onlysign TEXT NOT NULL DEFAULT '',
    ext_url TEXT NOT NULL DEFAULT '',
    ext_docket TEXT NOT NULL DEFAULT '',
    ext_marketprice REAL NOT NULL DEFAULT 0,
    ext_shopprice REAL NOT NULL DEFAULT 0,
    ext_standard TEXT NOT NULL DEFAULT '',
    ext_number TEXT NOT NULL DEFAULT '',
    ext_size TEXT NOT NULL DEFAULT '',
    ext_0 TEXT NOT NULL DEFAULT '',
    ext_1 TEXT NOT NULL DEFAULT '',
    ext_2 TEXT NOT NULL DEFAULT '',
    ext_3 TEXT NOT NULL DEFAULT '',
    ext_4 TEXT NOT NULL DEFAULT '',
    ext_5 TEXT NOT NULL DEFAULT '',
    ext_6 TEXT NOT NULL DEFAULT '',
    ext_7 TEXT NOT NULL DEFAULT '',
    ext_8 TEXT NOT NULL DEFAULT '',
    ext_9 TEXT NOT NULL DEFAULT '',
    ifcheck INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (id, cateid)
);

-- Table: sino_msg_content
CREATE TABLE IF NOT EXISTS sino_msg_content (
    id INTEGER PRIMARY KEY NOT NULL,
    cateid INTEGER NOT NULL DEFAULT 0,
    content TEXT NOT NULL
);

-- Table: sino_nav
CREATE TABLE IF NOT EXISTS sino_nav (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL DEFAULT '',
    css TEXT NOT NULL DEFAULT '',
    url TEXT NOT NULL DEFAULT '',
    target TEXT NOT NULL DEFAULT '',
    taxis INTEGER NOT NULL DEFAULT 255,
    language INTEGER NOT NULL DEFAULT 0
);

-- Table: sino_notice
CREATE TABLE IF NOT EXISTS sino_notice (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    language INTEGER NOT NULL DEFAULT 0,
    subject TEXT NOT NULL DEFAULT '',
    url TEXT NOT NULL DEFAULT '',
    content TEXT NOT NULL,
    postdate INTEGER NOT NULL DEFAULT 0
);

-- Table: sino_order
CREATE TABLE IF NOT EXISTS sino_order (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sn TEXT NOT NULL DEFAULT '',
    userid INTEGER NOT NULL DEFAULT 0,
    user TEXT NOT NULL DEFAULT '',
    msgid INTEGER NOT NULL DEFAULT 0,
    subject TEXT NOT NULL DEFAULT '',
    msgcount INTEGER NOT NULL DEFAULT 0,
    unitprice REAL NOT NULL DEFAULT 0,
    totalprice REAL NOT NULL DEFAULT 0,
    note TEXT NOT NULL DEFAULT '',
    contactmode TEXT NOT NULL DEFAULT '',
    address TEXT NOT NULL DEFAULT '',
    zipcode TEXT NOT NULL DEFAULT '',
    postdate INTEGER NOT NULL DEFAULT 0,
    email TEXT NOT NULL DEFAULT '',
    status INTEGER NOT NULL DEFAULT 0
);

-- Table: sino_special
CREATE TABLE IF NOT EXISTS sino_special (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    typeid INTEGER NOT NULL DEFAULT 0,
    subject TEXT NOT NULL DEFAULT '',
    style TEXT NOT NULL DEFAULT '',
    content TEXT NOT NULL,
    url TEXT NOT NULL DEFAULT '',
    taxis INTEGER NOT NULL DEFAULT 255,
    language INTEGER NOT NULL DEFAULT 0,
    ifcheck INTEGER NOT NULL DEFAULT 0
);

-- Table: sino_sysgroup
CREATE TABLE IF NOT EXISTS sino_sysgroup (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    groupname TEXT NOT NULL DEFAULT '',
    isext_url INTEGER NOT NULL DEFAULT 0,
    isext_docket INTEGER NOT NULL DEFAULT 0,
    isext_price INTEGER NOT NULL DEFAULT 0,
    isext_standard INTEGER NOT NULL DEFAULT 0,
    isext_number INTEGER NOT NULL DEFAULT 0,
    isext_size INTEGER NOT NULL DEFAULT 0,
    isext_download INTEGER NOT NULL DEFAULT 0,
    ext_0_name TEXT NOT NULL DEFAULT '',
    ext_1_name TEXT NOT NULL DEFAULT '',
    ext_2_name TEXT NOT NULL DEFAULT '',
    ext_3_name TEXT NOT NULL DEFAULT '',
    ext_4_name TEXT NOT NULL DEFAULT '',
    ext_5_name TEXT NOT NULL DEFAULT '',
    ext_6_name TEXT NOT NULL DEFAULT '',
    ext_7_name TEXT NOT NULL DEFAULT '',
    ext_8_name TEXT NOT NULL DEFAULT '',
    ext_9_name TEXT NOT NULL DEFAULT '',
    sign TEXT NOT NULL DEFAULT '',
    tplindex TEXT NOT NULL DEFAULT '',
    tpllist TEXT NOT NULL DEFAULT '',
    tplmsg TEXT NOT NULL DEFAULT '',
    is_thumb INTEGER NOT NULL DEFAULT 0
);

-- Table: sino_tpl
CREATE TABLE IF NOT EXISTS sino_tpl (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL DEFAULT '',
    folder TEXT NOT NULL DEFAULT '',
    taxis INTEGER NOT NULL DEFAULT 255,
    language INTEGER NOT NULL DEFAULT 0,
    isdefault INTEGER NOT NULL DEFAULT 0
);

-- Table: sino_upfiles
CREATE TABLE IF NOT EXISTS sino_upfiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filetype TEXT NOT NULL DEFAULT '',
    tmpname TEXT NOT NULL DEFAULT '',
    filename TEXT NOT NULL DEFAULT '',
    folder TEXT NOT NULL DEFAULT '',
    postdate INTEGER NOT NULL DEFAULT 0,
    thumbfile TEXT NOT NULL DEFAULT '',
    markfile TEXT NOT NULL DEFAULT ''
);

-- Table: sino_vote
CREATE TABLE IF NOT EXISTS sino_vote (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    voteid INTEGER NOT NULL DEFAULT 0,
    subject TEXT NOT NULL DEFAULT '',
    vtype TEXT NOT NULL DEFAULT '',
    vcount INTEGER NOT NULL DEFAULT 0,
    language INTEGER NOT NULL DEFAULT 0,
    ifcheck INTEGER NOT NULL DEFAULT 0
);