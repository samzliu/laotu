drop table if exists user;
create table user (
  user_id integer primary key autoincrement,
  email text not null,
  pw_hash text not null,
  name text not null,
  address text not null,
  phone varchar(15) not null
);

drop table if exists producer;
create table producer (
    producer_id integer primary key autoincrement,
    user_name text not null,
    email text,
    pw_hash text,
    location text
);

drop table if exists product;
create table product (
    product_id integer primary key autoincrement,
    title text not null,
    category text not null,
    quantity integer not null,
    price decimal(7,2) not null,
    description text not null,
    producer_id integer not null,
    standard_geo text,
    standard_producer text,
    standard_raw text,
    standard_production text,
    standard_storage text,
    standard_tech text,
    standard_package text,
    standard_price text,
    FOREIGN KEY (producer_id) REFERENCES producer(producer_id)
);

drop table if exists standards;
create table standards )
    standard_id integer primary key autoincrement,
    product_id integer unique FOREIGN KEY REFERENCES product(producer_id)
    organic_cert_1 boolean default 0
    organic_cert_2 boolean default 0
    organic_cert_3 boolean default 0
    organic_cert_4 boolean default 0
    organic_cert_5 boolean default 0
    organic_cert_6 boolean default 0
    organic_cert_7 boolean default 0
    organic_cert_8 boolean default 0
    quality_cert_1 boolean default 0
    quality_cert_2 boolean default 0
    producer_benifit_1 boolean default 0
    producer_benifit_2 boolean default 0
    producer_benifit_3 boolean default 0
    producer_benifit_4 boolean default 0
    producer_benifit_5 boolean default 0
    producer_benifit_6 boolean default 0
    consumer_benifit_1 boolean default 0
    local_1 boolean default 0
    local_2 boolean default 0
    local_3 boolean default 0
    package_1 boolean default 0
    package_2 boolean default 0
    ethnic_1 boolean default 0
    ethnic_2 boolean default 0
    ethnic_3 boolean default 0
    ethnic_4 boolean default 0
    ethnic_5 boolean default 0
    ethnic_6 boolean default 0
    ethnic_7 boolean default 0
    ethnic_8 boolean default 0
    ethnic_9 boolean default 0
    ethnic_10 boolean default 0
    production_1 boolean default 0
    production_2 boolean default 0
    production_3 boolean default 0
    production_4 boolean default 0
    production_5 boolean default 0
    craft_1 boolean default 0
    craft_2 boolean default 0
    craft_3 boolean default 0
    craft_4 boolean default 0
);

drop table if exists trans;
create table trans (
    trans_id integer primary key autoincrement,
    product_id integer not null,
    user_id integer not null,
    trans_date date not null,
    amount decimal(7,2) not null,
    FOREIGN KEY (product_id) REFERENCES product(producer_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

drop table if exists cart;
create table cart (
    user_id integer not null references user(user_id),
    product_id integer not null references product(product_id),
    quantity integer not null,
    PRIMARY KEY (user_id, product_id)
);



-- drop table if exists follower;
-- create table follower (
--   who_id integer,
--   whom_id integer
-- );
--
-- drop table if exists message;
-- create table message (
--   message_id integer primary key autoincrement,
--   author_id integer not null,
--   text text not null,
--   pub_date integer
-- );
