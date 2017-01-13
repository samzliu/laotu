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
    FOREIGN KEY (producer_id) REFERENCES producer(producer_id)
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

drop table if exists tag;
create table tag (
    tag_id integer primary key autoincrement,
    name text not null,
    importance integer not null   
);
