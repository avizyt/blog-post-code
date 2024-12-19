DB_SCHEMA = """
BEGIN;


CREATE TABLE IF NOT EXISTS public.actor
(
    actor_id serial NOT NULL,
    first_name character varying(45) COLLATE pg_catalog."default" NOT NULL,
    last_name character varying(45) COLLATE pg_catalog."default" NOT NULL,
    last_update timestamp without time zone NOT NULL DEFAULT now(),
    CONSTRAINT actor_pkey PRIMARY KEY (actor_id)
);

CREATE TABLE IF NOT EXISTS public.address
(
    address_id serial NOT NULL,
    address character varying(50) COLLATE pg_catalog."default" NOT NULL,
    address2 character varying(50) COLLATE pg_catalog."default",
    district character varying(20) COLLATE pg_catalog."default" NOT NULL,
    city_id smallint NOT NULL,
    postal_code character varying(10) COLLATE pg_catalog."default",
    phone character varying(20) COLLATE pg_catalog."default" NOT NULL,
    last_update timestamp without time zone NOT NULL DEFAULT now(),
    CONSTRAINT address_pkey PRIMARY KEY (address_id)
);

CREATE TABLE IF NOT EXISTS public.category
(
    category_id serial NOT NULL,
    name character varying(25) COLLATE pg_catalog."default" NOT NULL,
    last_update timestamp without time zone NOT NULL DEFAULT now(),
    CONSTRAINT category_pkey PRIMARY KEY (category_id)
);

CREATE TABLE IF NOT EXISTS public.city
(
    city_id serial NOT NULL,
    city character varying(50) COLLATE pg_catalog."default" NOT NULL,
    country_id smallint NOT NULL,
    last_update timestamp without time zone NOT NULL DEFAULT now(),
    CONSTRAINT city_pkey PRIMARY KEY (city_id)
);

CREATE TABLE IF NOT EXISTS public.country
(
    country_id serial NOT NULL,
    country character varying(50) COLLATE pg_catalog."default" NOT NULL,
    last_update timestamp without time zone NOT NULL DEFAULT now(),
    CONSTRAINT country_pkey PRIMARY KEY (country_id)
);

CREATE TABLE IF NOT EXISTS public.customer
(
    customer_id serial NOT NULL,
    store_id smallint NOT NULL,
    first_name character varying(45) COLLATE pg_catalog."default" NOT NULL,
    last_name character varying(45) COLLATE pg_catalog."default" NOT NULL,
    email character varying(50) COLLATE pg_catalog."default",
    address_id smallint NOT NULL,
    activebool boolean NOT NULL DEFAULT true,
    create_date date NOT NULL DEFAULT ('now'::text)::date,
    last_update timestamp without time zone DEFAULT now(),
    active integer,
    CONSTRAINT customer_pkey PRIMARY KEY (customer_id)
);

CREATE TABLE IF NOT EXISTS public.film
(
    film_id serial NOT NULL,
    title character varying(255) COLLATE pg_catalog."default" NOT NULL,
    description text COLLATE pg_catalog."default",
    release_year year,
    language_id smallint NOT NULL,
    rental_duration smallint NOT NULL DEFAULT 3,
    rental_rate numeric(4, 2) NOT NULL DEFAULT 4.99,
    length smallint,
    replacement_cost numeric(5, 2) NOT NULL DEFAULT 19.99,
    rating mpaa_rating DEFAULT 'G'::mpaa_rating,
    last_update timestamp without time zone NOT NULL DEFAULT now(),
    special_features text[] COLLATE pg_catalog."default",
    fulltext tsvector NOT NULL,
    CONSTRAINT film_pkey PRIMARY KEY (film_id)
);

CREATE TABLE IF NOT EXISTS public.film_actor
(
    actor_id smallint NOT NULL,
    film_id smallint NOT NULL,
    last_update timestamp without time zone NOT NULL DEFAULT now(),
    CONSTRAINT film_actor_pkey PRIMARY KEY (actor_id, film_id)
);

CREATE TABLE IF NOT EXISTS public.film_category
(
    film_id smallint NOT NULL,
    category_id smallint NOT NULL,
    last_update timestamp without time zone NOT NULL DEFAULT now(),
    CONSTRAINT film_category_pkey PRIMARY KEY (film_id, category_id)
);

CREATE TABLE IF NOT EXISTS public.inventory
(
    inventory_id serial NOT NULL,
    film_id smallint NOT NULL,
    store_id smallint NOT NULL,
    last_update timestamp without time zone NOT NULL DEFAULT now(),
    CONSTRAINT inventory_pkey PRIMARY KEY (inventory_id)
);

CREATE TABLE IF NOT EXISTS public.language
(
    language_id serial NOT NULL,
    name character(20) COLLATE pg_catalog."default" NOT NULL,
    last_update timestamp without time zone NOT NULL DEFAULT now(),
    CONSTRAINT language_pkey PRIMARY KEY (language_id)
);

CREATE TABLE IF NOT EXISTS public.payment
(
    payment_id serial NOT NULL,
    customer_id smallint NOT NULL,
    staff_id smallint NOT NULL,
    rental_id integer NOT NULL,
    amount numeric(5, 2) NOT NULL,
    payment_date timestamp without time zone NOT NULL,
    CONSTRAINT payment_pkey PRIMARY KEY (payment_id)
);

CREATE TABLE IF NOT EXISTS public.rental
(
    rental_id serial NOT NULL,
    rental_date timestamp without time zone NOT NULL,
    inventory_id integer NOT NULL,
    customer_id smallint NOT NULL,
    return_date timestamp without time zone,
    staff_id smallint NOT NULL,
    last_update timestamp without time zone NOT NULL DEFAULT now(),
    CONSTRAINT rental_pkey PRIMARY KEY (rental_id)
);

CREATE TABLE IF NOT EXISTS public.staff
(
    staff_id serial NOT NULL,
    first_name character varying(45) COLLATE pg_catalog."default" NOT NULL,
    last_name character varying(45) COLLATE pg_catalog."default" NOT NULL,
    address_id smallint NOT NULL,
    email character varying(50) COLLATE pg_catalog."default",
    store_id smallint NOT NULL,
    active boolean NOT NULL DEFAULT true,
    username character varying(16) COLLATE pg_catalog."default" NOT NULL,
    password character varying(40) COLLATE pg_catalog."default",
    last_update timestamp without time zone NOT NULL DEFAULT now(),
    picture bytea,
    CONSTRAINT staff_pkey PRIMARY KEY (staff_id)
);

CREATE TABLE IF NOT EXISTS public.store
(
    store_id serial NOT NULL,
    manager_staff_id smallint NOT NULL,
    address_id smallint NOT NULL,
    last_update timestamp without time zone NOT NULL DEFAULT now(),
    CONSTRAINT store_pkey PRIMARY KEY (store_id)
);

ALTER TABLE IF EXISTS public.address
    ADD CONSTRAINT fk_address_city FOREIGN KEY (city_id)
    REFERENCES public.city (city_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;
CREATE INDEX IF NOT EXISTS idx_fk_city_id
    ON public.address(city_id);


ALTER TABLE IF EXISTS public.city
    ADD CONSTRAINT fk_city FOREIGN KEY (country_id)
    REFERENCES public.country (country_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;
CREATE INDEX IF NOT EXISTS idx_fk_country_id
    ON public.city(country_id);


ALTER TABLE IF EXISTS public.customer
    ADD CONSTRAINT customer_address_id_fkey FOREIGN KEY (address_id)
    REFERENCES public.address (address_id) MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE RESTRICT;
CREATE INDEX IF NOT EXISTS idx_fk_address_id
    ON public.customer(address_id);


ALTER TABLE IF EXISTS public.film
    ADD CONSTRAINT film_language_id_fkey FOREIGN KEY (language_id)
    REFERENCES public.language (language_id) MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE RESTRICT;
CREATE INDEX IF NOT EXISTS idx_fk_language_id
    ON public.film(language_id);


ALTER TABLE IF EXISTS public.film_actor
    ADD CONSTRAINT film_actor_actor_id_fkey FOREIGN KEY (actor_id)
    REFERENCES public.actor (actor_id) MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE RESTRICT;


ALTER TABLE IF EXISTS public.film_actor
    ADD CONSTRAINT film_actor_film_id_fkey FOREIGN KEY (film_id)
    REFERENCES public.film (film_id) MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE RESTRICT;
CREATE INDEX IF NOT EXISTS idx_fk_film_id
    ON public.film_actor(film_id);


ALTER TABLE IF EXISTS public.film_category
    ADD CONSTRAINT film_category_category_id_fkey FOREIGN KEY (category_id)
    REFERENCES public.category (category_id) MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE RESTRICT;


ALTER TABLE IF EXISTS public.film_category
    ADD CONSTRAINT film_category_film_id_fkey FOREIGN KEY (film_id)
    REFERENCES public.film (film_id) MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE RESTRICT;


ALTER TABLE IF EXISTS public.inventory
    ADD CONSTRAINT inventory_film_id_fkey FOREIGN KEY (film_id)
    REFERENCES public.film (film_id) MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE RESTRICT;


ALTER TABLE IF EXISTS public.payment
    ADD CONSTRAINT payment_customer_id_fkey FOREIGN KEY (customer_id)
    REFERENCES public.customer (customer_id) MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE RESTRICT;
CREATE INDEX IF NOT EXISTS idx_fk_customer_id
    ON public.payment(customer_id);


ALTER TABLE IF EXISTS public.payment
    ADD CONSTRAINT payment_rental_id_fkey FOREIGN KEY (rental_id)
    REFERENCES public.rental (rental_id) MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS idx_fk_rental_id
    ON public.payment(rental_id);


ALTER TABLE IF EXISTS public.payment
    ADD CONSTRAINT payment_staff_id_fkey FOREIGN KEY (staff_id)
    REFERENCES public.staff (staff_id) MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE RESTRICT;
CREATE INDEX IF NOT EXISTS idx_fk_staff_id
    ON public.payment(staff_id);


ALTER TABLE IF EXISTS public.rental
    ADD CONSTRAINT rental_customer_id_fkey FOREIGN KEY (customer_id)
    REFERENCES public.customer (customer_id) MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE RESTRICT;


ALTER TABLE IF EXISTS public.rental
    ADD CONSTRAINT rental_inventory_id_fkey FOREIGN KEY (inventory_id)
    REFERENCES public.inventory (inventory_id) MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE RESTRICT;
CREATE INDEX IF NOT EXISTS idx_fk_inventory_id
    ON public.rental(inventory_id);


ALTER TABLE IF EXISTS public.rental
    ADD CONSTRAINT rental_staff_id_key FOREIGN KEY (staff_id)
    REFERENCES public.staff (staff_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.staff
    ADD CONSTRAINT staff_address_id_fkey FOREIGN KEY (address_id)
    REFERENCES public.address (address_id) MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE RESTRICT;


ALTER TABLE IF EXISTS public.store
    ADD CONSTRAINT store_address_id_fkey FOREIGN KEY (address_id)
    REFERENCES public.address (address_id) MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE RESTRICT;


ALTER TABLE IF EXISTS public.store
    ADD CONSTRAINT store_manager_staff_id_fkey FOREIGN KEY (manager_staff_id)
    REFERENCES public.staff (staff_id) MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE RESTRICT;
CREATE INDEX IF NOT EXISTS idx_unq_manager_staff_id
    ON public.store(manager_staff_id);

END;

"""
