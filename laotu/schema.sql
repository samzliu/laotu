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
    pw_hash text not null,
    location text
);

drop table if exists product;
create table product (
    product_id integer primary key autoincrement,
    title text not null,
    category text not null,
    quantity integer not null,
    price decimal(7,2) not null,
    location text not null,
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

drop table if exists follower;
create table follower (
  who_id integer,
  whom_id integer
);

drop table if exists message;
create table message (
  message_id integer primary key autoincrement,
  author_id integer not null,
  text text not null,
  pub_date integer
);
