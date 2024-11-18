--
-- PostgreSQL database dump
--

-- Dumped from database version 14.13 (Ubuntu 14.13-0ubuntu0.22.04.1)
-- Dumped by pg_dump version 14.13 (Ubuntu 14.13-0ubuntu0.22.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: atomic_schema; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA atomic_schema;


ALTER SCHEMA atomic_schema OWNER TO postgres;

--
-- Name: dbff_schema; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA dbff_schema;


ALTER SCHEMA dbff_schema OWNER TO postgres;

--
-- Name: intarray; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS intarray WITH SCHEMA public;


--
-- Name: EXTENSION intarray; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION intarray IS 'functions, operators, and index support for 1-D arrays of integers';


--
-- Name: pg_stat_statements; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_stat_statements WITH SCHEMA public;


--
-- Name: EXTENSION pg_stat_statements; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_stat_statements IS 'track planning and execution statistics of all SQL statements executed';


--
-- Name: pgstattuple; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgstattuple WITH SCHEMA public;


--
-- Name: EXTENSION pgstattuple; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgstattuple IS 'show tuple-level statistics';


--
-- Name: attribute; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.attribute AS (
	name character varying(64),
	type character varying(12)
);


ALTER TYPE public.attribute OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: account_value_actions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.account_value_actions (
    account character varying(13),
    action_name character varying(13),
    list_name character varying(13),
    "values" character varying(13)[],
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    added boolean DEFAULT false
);


ALTER TABLE public.account_value_actions OWNER TO postgres;

--
-- Name: asset_mints; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.asset_mints (
    asset_id bigint,
    template_id integer,
    mint integer
);


ALTER TABLE public.asset_mints OWNER TO postgres;

--
-- Name: assets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.assets (
    asset_id bigint NOT NULL,
    contract character varying(12),
    collection character varying(12),
    schema character varying(16),
    owner character varying(12),
    template_id integer,
    name_id integer,
    image_id integer,
    video_id integer,
    block_num bigint,
    seq bigint,
    "timestamp" timestamp without time zone,
    transferred timestamp without time zone,
    burnable boolean,
    transferable boolean,
    attribute_ids integer[],
    immutable_data_id integer,
    mutable_data_id integer,
    burned boolean DEFAULT false,
    mint integer
);


ALTER TABLE public.assets OWNER TO postgres;

--
-- Name: atomicassets_burns; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.atomicassets_burns (
    asset_id bigint,
    burner character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.atomicassets_burns OWNER TO postgres;

--
-- Name: atomicassets_burns_reversed; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.atomicassets_burns_reversed (
    asset_id bigint,
    burner character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.atomicassets_burns_reversed OWNER TO postgres;

--
-- Name: atomicassets_offer_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.atomicassets_offer_logs (
    offer_id bigint,
    sender character varying(13),
    recipient character varying(13),
    sender_asset_ids bigint[],
    recipient_asset_ids bigint[],
    status character varying(12),
    memo_id integer,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.atomicassets_offer_logs OWNER TO postgres;

--
-- Name: atomicassets_offer_updates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.atomicassets_offer_updates (
    offer_id bigint,
    status character varying(12),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.atomicassets_offer_updates OWNER TO postgres;

--
-- Name: atomicassets_offers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.atomicassets_offers (
    offer_id bigint,
    sender character varying(13),
    recipient character varying(13),
    sender_asset_ids bigint[],
    recipient_asset_ids bigint[],
    status character varying(13),
    memo_id integer,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.atomicassets_offers OWNER TO postgres;

--
-- Name: atomicassets_updates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.atomicassets_updates (
    asset_id bigint,
    new_mdata_id integer,
    old_mdata_id integer,
    applied boolean DEFAULT false,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.atomicassets_updates OWNER TO postgres;

--
-- Name: atomicassets_updates_reversed; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.atomicassets_updates_reversed (
    asset_id bigint,
    new_mdata_id integer,
    old_mdata_id integer,
    applied boolean,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.atomicassets_updates_reversed OWNER TO postgres;

--
-- Name: atomicmarket_accept_buy_offers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.atomicmarket_accept_buy_offers (
    buyoffer_id bigint,
    expected_asset_ids bigint[],
    expected_price double precision,
    taker_marketplace character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.atomicmarket_accept_buy_offers OWNER TO postgres;

--
-- Name: atomicmarket_auction_cancels; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.atomicmarket_auction_cancels (
    auction_id bigint,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.atomicmarket_auction_cancels OWNER TO postgres;

--
-- Name: atomicmarket_buy_offers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.atomicmarket_buy_offers (
    buyoffer_id bigint,
    buyer character varying(13),
    recipient character varying(13),
    price double precision,
    currency character varying(13),
    asset_ids bigint[],
    memo_id integer,
    maker_marketplace character varying(13),
    collection character varying(13),
    collection_fee double precision,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.atomicmarket_buy_offers OWNER TO postgres;

--
-- Name: atomicmarket_buy_offers_listings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.atomicmarket_buy_offers_listings (
    buyoffer_id bigint,
    buyer character varying(13),
    recipient character varying(13),
    price double precision,
    currency character varying(13),
    asset_ids bigint[],
    memo_id integer,
    maker_marketplace character varying(13),
    collection character varying(13),
    collection_fee double precision,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.atomicmarket_buy_offers_listings OWNER TO postgres;

--
-- Name: atomicmarket_cancel_buy_offers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.atomicmarket_cancel_buy_offers (
    buyoffer_id bigint,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.atomicmarket_cancel_buy_offers OWNER TO postgres;

--
-- Name: atomicmarket_cancel_template_buy_offers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.atomicmarket_cancel_template_buy_offers (
    buyoffer_id bigint,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.atomicmarket_cancel_template_buy_offers OWNER TO postgres;

--
-- Name: atomicmarket_cancels; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.atomicmarket_cancels (
    block_num bigint,
    seq bigint,
    "timestamp" timestamp without time zone,
    listing_id bigint
);


ALTER TABLE public.atomicmarket_cancels OWNER TO postgres;

--
-- Name: atomicmarket_decline_buy_offers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.atomicmarket_decline_buy_offers (
    buyoffer_id bigint,
    memo_id integer,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.atomicmarket_decline_buy_offers OWNER TO postgres;

--
-- Name: atomicmarket_fulfill_template_buy_offers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.atomicmarket_fulfill_template_buy_offers (
    buyoffer_id bigint,
    asset_id bigint,
    seller character varying(13),
    price double precision,
    currency character varying(12),
    taker character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.atomicmarket_fulfill_template_buy_offers OWNER TO postgres;

--
-- Name: atomicmarket_listings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.atomicmarket_listings (
    asset_ids bigint[],
    seller character varying(13),
    price double precision,
    currency character varying(12),
    listing_id bigint,
    maker character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.atomicmarket_listings OWNER TO postgres;

--
-- Name: atomicmarket_purchases; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.atomicmarket_purchases (
    buyer character varying(13),
    block_num bigint,
    seq bigint,
    "timestamp" timestamp without time zone,
    listing_id bigint,
    taker character varying(13)
);


ALTER TABLE public.atomicmarket_purchases OWNER TO postgres;

--
-- Name: atomicmarket_sale_starts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.atomicmarket_sale_starts (
    listing_id bigint,
    offer_id bigint,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.atomicmarket_sale_starts OWNER TO postgres;

--
-- Name: atomicmarket_template_buy_offer_listings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.atomicmarket_template_buy_offer_listings (
    buyoffer_id bigint NOT NULL,
    buyer character varying(13),
    price double precision,
    currency character varying(12),
    template_id bigint,
    maker character varying(13),
    collection character varying(13),
    collection_fee double precision,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.atomicmarket_template_buy_offer_listings OWNER TO postgres;

--
-- Name: atomicmarket_template_buy_offers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.atomicmarket_template_buy_offers (
    buyoffer_id bigint NOT NULL,
    buyer character varying(13),
    price double precision,
    currency character varying(12),
    template_id bigint,
    maker character varying(13),
    collection character varying(13),
    collection_fee double precision,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.atomicmarket_template_buy_offers OWNER TO postgres;

--
-- Name: attributes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.attributes (
    attribute_id integer NOT NULL,
    collection character varying(13),
    schema character varying(16),
    attribute_name character varying(64),
    string_value character varying(256),
    int_value bigint,
    float_value double precision,
    bool_value boolean
);


ALTER TABLE public.attributes OWNER TO postgres;

--
-- Name: listings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.listings (
    asset_ids bigint[],
    collection character varying(13),
    seller character varying(13),
    market character varying(13),
    maker character varying(13),
    price double precision,
    currency character varying(12),
    listing_id bigint,
    sale_id bigint NOT NULL,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    estimated_wax_price double precision
);


ALTER TABLE public.listings OWNER TO postgres;

--
-- Name: usd_prices; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usd_prices (
    "timestamp" timestamp without time zone,
    usd double precision
);


ALTER TABLE public.usd_prices OWNER TO postgres;

--
-- Name: attribute_floors_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.attribute_floors_mv AS
 SELECT att.attribute_id,
    min(
        CASE
            WHEN ((s.currency)::text = 'WAX'::text) THEN s.price
            ELSE (s.price / ( SELECT usd_prices.usd
               FROM public.usd_prices
              ORDER BY usd_prices."timestamp" DESC
             LIMIT 1))
        END) AS floor_wax,
    min(
        CASE
            WHEN ((s.currency)::text = 'USD'::text) THEN s.price
            ELSE (s.price * ( SELECT usd_prices.usd
               FROM public.usd_prices
              ORDER BY usd_prices."timestamp" DESC
             LIMIT 1))
        END) AS floor_usd
   FROM ((public.listings s
     JOIN public.assets a ON ((a.asset_id = ANY (s.asset_ids))))
     JOIN public.attributes att ON ((att.attribute_id = ANY (a.attribute_ids))))
  GROUP BY att.attribute_id
  WITH NO DATA;


ALTER TABLE public.attribute_floors_mv OWNER TO postgres;

--
-- Name: attribute_stats; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.attribute_stats (
    collection character varying(13),
    schema character varying(13),
    attribute_id integer,
    total integer,
    avg_wax_price double precision,
    avg_usd_price double precision,
    last_sold_wax double precision,
    last_sold_usd double precision,
    last_sold_seq bigint,
    last_sold_block_num bigint,
    floor_wax double precision,
    floor_usd double precision,
    volume_wax double precision,
    volume_usd double precision,
    num_sales integer,
    total_schema integer,
    rarity_score double precision
);


ALTER TABLE public.attribute_stats OWNER TO postgres;

--
-- Name: attributes_attribute_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.attributes_attribute_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.attributes_attribute_id_seq OWNER TO postgres;

--
-- Name: attributes_attribute_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.attributes_attribute_id_seq OWNED BY public.attributes.attribute_id;


--
-- Name: auction_bids; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auction_bids (
    bidder character varying(13),
    bid double precision,
    currency character varying(12),
    auction_id bigint,
    taker character varying(13),
    market character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.auction_bids OWNER TO postgres;

--
-- Name: auction_claims; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auction_claims (
    auction_id bigint,
    market character varying(13),
    claimer character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.auction_claims OWNER TO postgres;

--
-- Name: auction_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auction_logs (
    auction_id bigint,
    asset_ids bigint[],
    seller character varying(13),
    end_time timestamp without time zone,
    start_bid double precision,
    current_bid double precision,
    currency character varying(12),
    maker character varying(13),
    market character varying(13),
    active boolean,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.auction_logs OWNER TO postgres;

--
-- Name: auctions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auctions (
    auction_id bigint,
    asset_ids bigint[],
    seller character varying(13),
    end_time timestamp without time zone,
    start_bid double precision,
    current_bid double precision,
    currency character varying(12),
    maker character varying(13),
    market character varying(13),
    active boolean,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.auctions OWNER TO postgres;

--
-- Name: backed_assets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.backed_assets (
    asset_id bigint,
    amount double precision,
    currency character varying(12),
    backer character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.backed_assets OWNER TO postgres;

--
-- Name: badges; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.badges (
    collection character varying(13),
    name character varying(32),
    level integer,
    value character varying(32),
    "timestamp" timestamp without time zone
);


ALTER TABLE public.badges OWNER TO postgres;

--
-- Name: banners; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.banners (
    image character varying(256),
    url character varying(256),
    start_date timestamp without time zone,
    end_date timestamp without time zone,
    source character varying(12),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.banners OWNER TO postgres;

--
-- Name: blacklisted_collections; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.blacklisted_collections (
    collection character varying(13)
);


ALTER TABLE public.blacklisted_collections OWNER TO postgres;

--
-- Name: indexes; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.indexes AS
 SELECT t.relname AS table_name,
    i.relname AS index_name,
    a.attname AS column_name
   FROM pg_class t,
    pg_class i,
    pg_index ix,
    pg_attribute a
  WHERE ((t.oid = ix.indrelid) AND (i.oid = ix.indexrelid) AND (a.attrelid = t.oid) AND (a.attnum = ANY ((ix.indkey)::smallint[])) AND (t.relkind = 'r'::"char"))
  ORDER BY t.relname, i.relname;


ALTER TABLE public.indexes OWNER TO postgres;

--
-- Name: tables_with_block_num; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.tables_with_block_num AS
 SELECT t.table_schema,
    t.table_name
   FROM (information_schema.tables t
     JOIN information_schema.columns c ON ((((c.table_name)::name = (t.table_name)::name) AND ((c.table_schema)::name = (t.table_schema)::name))))
  WHERE (((c.column_name)::name = 'block_num'::name) AND ((t.table_schema)::name <> ALL (ARRAY['information_schema'::name, 'pg_catalog'::name])) AND ((t.table_type)::text = 'BASE TABLE'::text))
  ORDER BY t.table_schema;


ALTER TABLE public.tables_with_block_num OWNER TO postgres;

--
-- Name: block_num_index_creation; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.block_num_index_creation AS
 SELECT ((' CREATE INDEX ON '::text || (f.table_name)::text) || ' (block_num ASC) ;'::text) AS "?column?"
   FROM ( SELECT tables_with_block_num.table_name
           FROM public.tables_with_block_num
          WHERE (NOT ((tables_with_block_num.table_name)::name IN ( SELECT indexes.table_name
                   FROM public.indexes
                  WHERE (indexes.column_name = 'block_num'::name))))) f;


ALTER TABLE public.block_num_index_creation OWNER TO postgres;

--
-- Name: blocked_queries; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.blocked_queries AS
 SELECT pg_stat_activity.pid,
    pg_stat_activity.usename,
    pg_blocking_pids(pg_stat_activity.pid) AS blocked_by,
    pg_stat_activity.query AS blocked_query
   FROM pg_stat_activity
  WHERE (cardinality(pg_blocking_pids(pg_stat_activity.pid)) > 0);


ALTER TABLE public.blocked_queries OWNER TO postgres;

--
-- Name: sales_summary; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sales_summary (
    collection character varying(13),
    type character varying(10),
    wax_price double precision,
    usd_price double precision,
    num_items integer,
    buyer character varying(13),
    seller character varying(13),
    market character varying(13),
    taker character varying(13),
    maker character varying(13),
    listing_id bigint,
    "timestamp" timestamp without time zone,
    seq bigint,
    block_num bigint
);


ALTER TABLE public.sales_summary OWNER TO postgres;

--
-- Name: buyer_volumes_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.buyer_volumes_mv AS
 SELECT sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '1 day'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
            ELSE (0)::double precision
        END) AS wax_volume_1_day,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '1 day'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.usd_price
            ELSE (0)::double precision
        END) AS usd_volume_1_day,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '2 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
            ELSE (0)::double precision
        END) AS wax_volume_2_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '2 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.usd_price
            ELSE (0)::double precision
        END) AS usd_volume_2_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '3 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
            ELSE (0)::double precision
        END) AS wax_volume_3_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '3 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.usd_price
            ELSE (0)::double precision
        END) AS usd_volume_3_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '7 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
            ELSE (0)::double precision
        END) AS wax_volume_7_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '7 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.usd_price
            ELSE (0)::double precision
        END) AS usd_volume_7_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '14 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
            ELSE (0)::double precision
        END) AS wax_volume_14_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '14 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.usd_price
            ELSE (0)::double precision
        END) AS usd_volume_14_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '30 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
            ELSE (0)::double precision
        END) AS wax_volume_30_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '30 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.usd_price
            ELSE (0)::double precision
        END) AS usd_volume_30_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '60 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
            ELSE (0)::double precision
        END) AS wax_volume_60_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '60 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.usd_price
            ELSE (0)::double precision
        END) AS usd_volume_60_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '90 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
            ELSE (0)::double precision
        END) AS wax_volume_90_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '90 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.usd_price
            ELSE (0)::double precision
        END) AS usd_volume_90_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '180 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
            ELSE (0)::double precision
        END) AS wax_volume_180_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '180 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.usd_price
            ELSE (0)::double precision
        END) AS usd_volume_180_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '365 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
            ELSE (0)::double precision
        END) AS wax_volume_365_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '365 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.usd_price
            ELSE (0)::double precision
        END) AS usd_volume_365_days,
    sum(sales_summary.wax_price) AS wax_volume_all_time,
    sum(sales_summary.usd_price) AS usd_volume_all_time,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '1 day'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.num_items
            ELSE 0
        END) AS purchases_1_day,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '2 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.num_items
            ELSE 0
        END) AS purchases_2_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '3 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.num_items
            ELSE 0
        END) AS purchases_3_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '7 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.num_items
            ELSE 0
        END) AS purchases_7_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '14 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.num_items
            ELSE 0
        END) AS purchases_14_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '30 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.num_items
            ELSE 0
        END) AS purchases_30_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '60 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.num_items
            ELSE 0
        END) AS purchases_60_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '90 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.num_items
            ELSE 0
        END) AS purchases_90_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '180 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.num_items
            ELSE 0
        END) AS purchases_180_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '365 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.num_items
            ELSE 0
        END) AS purchases_365_days,
    sum(sales_summary.num_items) AS purchases_all_time,
    sales_summary.buyer AS user_name,
    sales_summary.type,
    sales_summary.collection
   FROM public.sales_summary
  GROUP BY sales_summary.buyer, sales_summary.type, sales_summary.collection
  WITH NO DATA;


ALTER TABLE public.buyer_volumes_mv OWNER TO postgres;

--
-- Name: buyoffer_balance_updates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.buyoffer_balance_updates (
    buyer character varying(12),
    balance double precision,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.buyoffer_balance_updates OWNER TO postgres;

--
-- Name: buyoffer_cancels; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.buyoffer_cancels (
    offer_id integer,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.buyoffer_cancels OWNER TO postgres;

--
-- Name: buyoffer_purchases; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.buyoffer_purchases (
    offer_id integer,
    asset_id bigint,
    price double precision,
    taker character varying(13),
    seller character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.buyoffer_purchases OWNER TO postgres;

--
-- Name: buyoffers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.buyoffers (
    offer_id integer,
    price double precision,
    currency character varying(12),
    buyer character varying(13),
    template_id integer,
    collection character varying(13),
    name_id integer,
    image_id integer,
    video_id integer,
    active boolean,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.buyoffers OWNER TO postgres;

--
-- Name: chronicle_transactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chronicle_transactions (
    transaction_id character varying(64),
    seq bigint NOT NULL,
    "timestamp" timestamp without time zone,
    block_num bigint,
    account character varying(13),
    action_name character varying(13),
    data json,
    ingested boolean DEFAULT false,
    actor character varying(13)
);


ALTER TABLE public.chronicle_transactions OWNER TO postgres;

--
-- Name: claimed_auctions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.claimed_auctions (
    auction_id bigint,
    asset_ids bigint[],
    seller character varying(13),
    claimer character varying(13),
    market character varying(13),
    maker character varying(13),
    taker character varying(13),
    final_bid double precision,
    currency character varying(12),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.claimed_auctions OWNER TO postgres;

--
-- Name: collection_account_updates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.collection_account_updates (
    collection character varying(13),
    account_to_add character varying(13),
    account_to_remove character varying(13),
    applied boolean DEFAULT false,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.collection_account_updates OWNER TO postgres;

--
-- Name: sales; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sales (
    asset_ids bigint[],
    collection character varying(13),
    seller character varying(13),
    buyer character varying(13),
    wax_price double precision,
    usd_price double precision,
    currency character varying(12),
    listing_id bigint,
    market character varying(13),
    maker character varying(13),
    taker character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.sales OWNER TO postgres;

--
-- Name: template_sales; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.template_sales (
    template_id integer,
    schema character varying(16),
    collection character varying(13),
    wax_price double precision,
    usd_price double precision,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.template_sales OWNER TO postgres;

--
-- Name: template_stats_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.template_stats_mv AS
 SELECT t1.template_id,
    t1.avg_wax_price,
    t1.avg_usd_price,
    t1.num_sales,
    t1.volume_wax,
    t1.volume_usd,
    t2.wax_price AS last_sold_wax,
    t2.usd_price AS last_sold_usd,
    t2.seq AS last_sold_seq,
    t2.block_num AS last_sold_block_num,
    t2."timestamp" AS last_sold_timestamp,
    s.listing_id AS last_sold_listing_id
   FROM ((( SELECT t1_1.template_id,
            avg(t1_1.wax_price) AS avg_wax_price,
            avg(t1_1.usd_price) AS avg_usd_price,
            count(1) AS num_sales,
            sum(t1_1.wax_price) AS volume_wax,
            sum(t1_1.usd_price) AS volume_usd
           FROM public.template_sales t1_1
          GROUP BY t1_1.template_id) t1
     LEFT JOIN public.template_sales t2 ON ((t2.seq = ( SELECT max(template_sales.seq) AS max
           FROM public.template_sales
          WHERE (template_sales.template_id = t1.template_id)))))
     LEFT JOIN public.sales s ON ((s.seq = t2.seq)))
  WITH NO DATA;


ALTER TABLE public.template_stats_mv OWNER TO postgres;

--
-- Name: collection_users_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.collection_users_mv AS
 SELECT a.collection,
    a.owner,
    count(1) AS num_assets,
    sum(template_stats_mv.avg_wax_price) AS wax_value,
    sum(template_stats_mv.avg_usd_price) AS usd_value
   FROM (public.assets a
     LEFT JOIN public.template_stats_mv USING (template_id))
  WHERE ((NOT a.burned) AND (a.owner IS NOT NULL))
  GROUP BY a.collection, a.owner
  WITH NO DATA;


ALTER TABLE public.collection_users_mv OWNER TO postgres;

--
-- Name: collection_assets_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.collection_assets_mv AS
 SELECT collection_users_mv.collection,
    sum(collection_users_mv.num_assets) AS num_assets
   FROM public.collection_users_mv
  GROUP BY collection_users_mv.collection
  WITH NO DATA;


ALTER TABLE public.collection_assets_mv OWNER TO postgres;

--
-- Name: collection_badges_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.collection_badges_mv AS
 SELECT b1.collection,
    json_agg(json_build_object('name', b1.name, 'value', b1.value, 'level', b1.level)) AS badges
   FROM public.badges b1
  GROUP BY b1.collection
  WITH NO DATA;


ALTER TABLE public.collection_badges_mv OWNER TO postgres;

--
-- Name: collection_fee_updates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.collection_fee_updates (
    collection character varying(13),
    new_market_fee double precision,
    old_market_fee double precision,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    applied boolean DEFAULT false
);


ALTER TABLE public.collection_fee_updates OWNER TO postgres;

--
-- Name: templates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.templates (
    template_id integer NOT NULL,
    collection character varying(13),
    schema character varying(16),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    name_id integer,
    image_id integer,
    video_id integer,
    max_supply bigint,
    burnable boolean,
    transferable boolean,
    num_assets integer,
    attribute_ids integer[],
    immutable_data_id integer
);


ALTER TABLE public.templates OWNER TO postgres;

--
-- Name: templates_minted_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.templates_minted_mv AS
 SELECT assets.template_id,
    count(1) AS num_minted,
    sum(
        CASE
            WHEN assets.burned THEN 1
            ELSE 0
        END) AS num_burned
   FROM public.assets
  WHERE (assets.template_id > 0)
  GROUP BY assets.template_id
  WITH NO DATA;


ALTER TABLE public.templates_minted_mv OWNER TO postgres;

--
-- Name: collection_market_cap_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.collection_market_cap_mv AS
 SELECT t.collection,
    sum((template_stats_mv.avg_wax_price * ((COALESCE(templates_minted_mv.num_minted, (0)::bigint) - COALESCE(templates_minted_mv.num_burned, (0)::bigint)))::double precision)) AS wax_market_cap,
    sum((template_stats_mv.avg_usd_price * ((COALESCE(templates_minted_mv.num_minted, (0)::bigint) - COALESCE(templates_minted_mv.num_burned, (0)::bigint)))::double precision)) AS usd_market_cap
   FROM ((public.templates t
     LEFT JOIN public.template_stats_mv USING (template_id))
     LEFT JOIN public.templates_minted_mv USING (template_id))
  GROUP BY t.collection
  WITH NO DATA;


ALTER TABLE public.collection_market_cap_mv OWNER TO postgres;

--
-- Name: collection_sales_by_date_before_2024_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.collection_sales_by_date_before_2024_mv AS
 SELECT sales_summary.collection,
    to_date(to_char(sales_summary."timestamp", 'YYYY/MM/DD'::text), 'YYYY/MM/DD'::text) AS to_date,
    sales_summary.type,
    sum(sales_summary.wax_price) AS wax_volume,
    sum(sales_summary.usd_price) AS usd_volume,
    count(DISTINCT sales_summary.buyer) AS buyers,
    count(DISTINCT sales_summary.seller) AS sellers,
    count(1) AS sales
   FROM public.sales_summary
  WHERE (sales_summary."timestamp" < '2024-01-01 00:00:00'::timestamp without time zone)
  GROUP BY sales_summary.collection, (to_date(to_char(sales_summary."timestamp", 'YYYY/MM/DD'::text), 'YYYY/MM/DD'::text)), sales_summary.type
  WITH NO DATA;


ALTER TABLE public.collection_sales_by_date_before_2024_mv OWNER TO postgres;

--
-- Name: collection_sales_by_date_from_2024_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.collection_sales_by_date_from_2024_mv AS
 SELECT sales_summary.collection,
    to_date(to_char(sales_summary."timestamp", 'YYYY/MM/DD'::text), 'YYYY/MM/DD'::text) AS to_date,
    sales_summary.type,
    sum(sales_summary.wax_price) AS wax_volume,
    sum(sales_summary.usd_price) AS usd_volume,
    count(DISTINCT sales_summary.buyer) AS buyers,
    count(DISTINCT sales_summary.seller) AS sellers,
    count(1) AS sales
   FROM public.sales_summary
  WHERE (sales_summary."timestamp" >= '2024-01-01 00:00:00'::timestamp without time zone)
  GROUP BY sales_summary.collection, (to_date(to_char(sales_summary."timestamp", 'YYYY/MM/DD'::text), 'YYYY/MM/DD'::text)), sales_summary.type
  WITH NO DATA;


ALTER TABLE public.collection_sales_by_date_from_2024_mv OWNER TO postgres;

--
-- Name: collection_sales_by_date_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.collection_sales_by_date_mv AS
 SELECT collection_sales_by_date_from_2024_mv.collection,
    collection_sales_by_date_from_2024_mv.to_date,
    collection_sales_by_date_from_2024_mv.type,
    collection_sales_by_date_from_2024_mv.wax_volume,
    collection_sales_by_date_from_2024_mv.usd_volume,
    collection_sales_by_date_from_2024_mv.buyers,
    collection_sales_by_date_from_2024_mv.sellers,
    collection_sales_by_date_from_2024_mv.sales
   FROM public.collection_sales_by_date_from_2024_mv
UNION ALL
 SELECT collection_sales_by_date_before_2024_mv.collection,
    collection_sales_by_date_before_2024_mv.to_date,
    collection_sales_by_date_before_2024_mv.type,
    collection_sales_by_date_before_2024_mv.wax_volume,
    collection_sales_by_date_before_2024_mv.usd_volume,
    collection_sales_by_date_before_2024_mv.buyers,
    collection_sales_by_date_before_2024_mv.sellers,
    collection_sales_by_date_before_2024_mv.sales
   FROM public.collection_sales_by_date_before_2024_mv
  WITH NO DATA;


ALTER TABLE public.collection_sales_by_date_mv OWNER TO postgres;

--
-- Name: tag_updates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tag_updates (
    tag_id integer,
    collection character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.tag_updates OWNER TO postgres;

--
-- Name: tags; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tags (
    tag_id integer NOT NULL,
    tag_name character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.tags OWNER TO postgres;

--
-- Name: tags_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.tags_mv AS
 SELECT b.collection,
    b.tag_id,
    t.tag_name
   FROM (( SELECT tag_updates.collection,
            tag_updates.tag_id
           FROM public.tag_updates) b
     LEFT JOIN public.tags t USING (tag_id))
  GROUP BY b.collection, b.tag_id, t.tag_name
  WITH NO DATA;


ALTER TABLE public.tags_mv OWNER TO postgres;

--
-- Name: collection_tag_ids_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.collection_tag_ids_mv AS
 SELECT tags_mv.collection,
    array_agg(tags_mv.tag_id) AS tag_ids
   FROM public.tags_mv
  GROUP BY tags_mv.collection
  WITH NO DATA;


ALTER TABLE public.collection_tag_ids_mv OWNER TO postgres;

--
-- Name: collection_updates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.collection_updates (
    collection character varying(13),
    new_name_id integer,
    old_name_id integer,
    new_description text,
    old_description text,
    new_url character varying(256),
    old_url character varying(256),
    new_image_id integer,
    old_image_id integer,
    new_socials text,
    old_socials text,
    new_creator_info text,
    old_creator_info text,
    new_images text,
    old_images text,
    applied boolean,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.collection_updates OWNER TO postgres;

--
-- Name: collection_user_count_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.collection_user_count_mv AS
 SELECT collection_users_mv.collection,
    count(1) AS num_users,
    sum(collection_users_mv.wax_value) AS wax_value,
    sum(collection_users_mv.usd_value) AS usd_value,
    sum(collection_users_mv.num_assets) AS num_assets
   FROM public.collection_users_mv
  GROUP BY collection_users_mv.collection
  WITH NO DATA;


ALTER TABLE public.collection_user_count_mv OWNER TO postgres;

--
-- Name: user_collection_volumes_14_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.user_collection_volumes_14_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales,
    t.collection,
    t.buyer,
    t.seller,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '14 days'::interval))
  GROUP BY t.collection, t.buyer, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.user_collection_volumes_14_mv OWNER TO postgres;

--
-- Name: collection_volumes_14_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.collection_volumes_14_mv AS
 SELECT sum(t.wax_volume) AS wax_volume,
    sum(t.wax_volume) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    sum(t.sales) AS sales,
    t.collection,
    t.type
   FROM public.user_collection_volumes_14_mv t
  GROUP BY t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.collection_volumes_14_mv OWNER TO postgres;

--
-- Name: user_collection_volumes_15_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.user_collection_volumes_15_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales,
    t.collection,
    t.buyer,
    t.seller,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '15 days'::interval))
  GROUP BY t.collection, t.buyer, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.user_collection_volumes_15_mv OWNER TO postgres;

--
-- Name: collection_volumes_15_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.collection_volumes_15_mv AS
 SELECT sum(t.wax_volume) AS wax_volume,
    sum(t.wax_volume) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    sum(t.sales) AS sales,
    t.collection,
    t.type
   FROM public.user_collection_volumes_15_mv t
  GROUP BY t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.collection_volumes_15_mv OWNER TO postgres;

--
-- Name: user_collection_volumes_180_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.user_collection_volumes_180_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales,
    t.collection,
    t.buyer,
    t.seller,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '180 days'::interval))
  GROUP BY t.collection, t.buyer, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.user_collection_volumes_180_mv OWNER TO postgres;

--
-- Name: collection_volumes_180_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.collection_volumes_180_mv AS
 SELECT sum(t.wax_volume) AS wax_volume,
    sum(t.wax_volume) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    sum(t.sales) AS sales,
    t.collection,
    t.type
   FROM public.user_collection_volumes_180_mv t
  GROUP BY t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.collection_volumes_180_mv OWNER TO postgres;

--
-- Name: user_collection_volumes_1_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.user_collection_volumes_1_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales,
    t.collection,
    t.buyer,
    t.seller,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '1 day'::interval))
  GROUP BY t.collection, t.buyer, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.user_collection_volumes_1_mv OWNER TO postgres;

--
-- Name: collection_volumes_1_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.collection_volumes_1_mv AS
 SELECT sum(t.wax_volume) AS wax_volume,
    sum(t.wax_volume) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    count(t.sales) AS sales,
    t.collection,
    t.type
   FROM public.user_collection_volumes_1_mv t
  GROUP BY t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.collection_volumes_1_mv OWNER TO postgres;

--
-- Name: user_collection_volumes_2_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.user_collection_volumes_2_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales,
    t.collection,
    t.buyer,
    t.seller,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '2 days'::interval))
  GROUP BY t.collection, t.buyer, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.user_collection_volumes_2_mv OWNER TO postgres;

--
-- Name: collection_volumes_2_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.collection_volumes_2_mv AS
 SELECT sum(t.wax_volume) AS wax_volume,
    sum(t.wax_volume) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    count(t.sales) AS sales,
    t.collection,
    t.type
   FROM public.user_collection_volumes_2_mv t
  GROUP BY t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.collection_volumes_2_mv OWNER TO postgres;

--
-- Name: user_collection_volumes_30_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.user_collection_volumes_30_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales,
    t.collection,
    t.buyer,
    t.seller,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '30 days'::interval))
  GROUP BY t.collection, t.buyer, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.user_collection_volumes_30_mv OWNER TO postgres;

--
-- Name: collection_volumes_30_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.collection_volumes_30_mv AS
 SELECT sum(t.wax_volume) AS wax_volume,
    sum(t.wax_volume) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    sum(t.sales) AS sales,
    t.collection,
    t.type
   FROM public.user_collection_volumes_30_mv t
  GROUP BY t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.collection_volumes_30_mv OWNER TO postgres;

--
-- Name: user_collection_volumes_365_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.user_collection_volumes_365_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales,
    t.collection,
    t.buyer,
    t.seller,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '365 days'::interval))
  GROUP BY t.collection, t.buyer, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.user_collection_volumes_365_mv OWNER TO postgres;

--
-- Name: collection_volumes_365_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.collection_volumes_365_mv AS
 SELECT sum(t.wax_volume) AS wax_volume,
    sum(t.wax_volume) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    sum(t.sales) AS sales,
    t.collection,
    t.type
   FROM public.user_collection_volumes_365_mv t
  GROUP BY t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.collection_volumes_365_mv OWNER TO postgres;

--
-- Name: user_collection_volumes_3_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.user_collection_volumes_3_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales,
    t.collection,
    t.buyer,
    t.seller,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '3 days'::interval))
  GROUP BY t.collection, t.buyer, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.user_collection_volumes_3_mv OWNER TO postgres;

--
-- Name: collection_volumes_3_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.collection_volumes_3_mv AS
 SELECT sum(t.wax_volume) AS wax_volume,
    sum(t.wax_volume) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    count(t.sales) AS sales,
    t.collection,
    t.type
   FROM public.user_collection_volumes_3_mv t
  GROUP BY t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.collection_volumes_3_mv OWNER TO postgres;

--
-- Name: user_collection_volumes_60_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.user_collection_volumes_60_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales,
    t.collection,
    t.buyer,
    t.seller,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '60 days'::interval))
  GROUP BY t.collection, t.buyer, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.user_collection_volumes_60_mv OWNER TO postgres;

--
-- Name: collection_volumes_60_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.collection_volumes_60_mv AS
 SELECT sum(t.wax_volume) AS wax_volume,
    sum(t.wax_volume) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    sum(t.sales) AS sales,
    t.collection,
    t.type
   FROM public.user_collection_volumes_60_mv t
  GROUP BY t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.collection_volumes_60_mv OWNER TO postgres;

--
-- Name: user_collection_volumes_7_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.user_collection_volumes_7_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales,
    t.collection,
    t.buyer,
    t.seller,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '7 days'::interval))
  GROUP BY t.collection, t.buyer, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.user_collection_volumes_7_mv OWNER TO postgres;

--
-- Name: collection_volumes_7_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.collection_volumes_7_mv AS
 SELECT sum(t.wax_volume) AS wax_volume,
    sum(t.wax_volume) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    sum(t.sales) AS sales,
    t.collection,
    t.type
   FROM public.user_collection_volumes_7_mv t
  GROUP BY t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.collection_volumes_7_mv OWNER TO postgres;

--
-- Name: user_collection_volumes_90_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.user_collection_volumes_90_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales,
    t.collection,
    t.buyer,
    t.seller,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '90 days'::interval))
  GROUP BY t.collection, t.buyer, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.user_collection_volumes_90_mv OWNER TO postgres;

--
-- Name: collection_volumes_90_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.collection_volumes_90_mv AS
 SELECT sum(t.wax_volume) AS wax_volume,
    sum(t.wax_volume) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    sum(t.sales) AS sales,
    t.collection,
    t.type
   FROM public.user_collection_volumes_90_mv t
  GROUP BY t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.collection_volumes_90_mv OWNER TO postgres;

--
-- Name: collection_volumes_from_2023_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.collection_volumes_from_2023_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales,
    t.collection,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > '2023-01-01 00:00:00'::timestamp without time zone)
  GROUP BY t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.collection_volumes_from_2023_mv OWNER TO postgres;

--
-- Name: collection_volumes_s_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.collection_volumes_s_mv AS
 SELECT sum(t.wax_volume_1_day) AS wax_volume_1_day,
    sum(t.usd_volume_1_day) AS usd_volume_1_day,
    sum(t.wax_volume_2_days) AS wax_volume_2_days,
    sum(t.usd_volume_2_days) AS usd_volume_2_days,
    sum(t.wax_volume_3_days) AS wax_volume_3_days,
    sum(t.usd_volume_3_days) AS usd_volume_3_days,
    sum(t.wax_volume_7_days) AS wax_volume_7_days,
    sum(t.usd_volume_7_days) AS usd_volume_7_days,
    count(t.purchases_1_day) AS purchases_1_day,
    sum(t.purchases_2_days) AS purchases_2_days,
    sum(t.purchases_3_days) AS purchases_3_days,
    sum(t.purchases_7_days) AS purchases_7_days,
    t.type,
    t.collection
   FROM ( SELECT
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '1 day'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
                    ELSE (0)::double precision
                END AS wax_volume_1_day,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '1 day'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.usd_price
                    ELSE (0)::double precision
                END AS usd_volume_1_day,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '2 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
                    ELSE (0)::double precision
                END AS wax_volume_2_days,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '2 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.usd_price
                    ELSE (0)::double precision
                END AS usd_volume_2_days,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '3 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
                    ELSE (0)::double precision
                END AS wax_volume_3_days,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '3 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.usd_price
                    ELSE (0)::double precision
                END AS usd_volume_3_days,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '7 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
                    ELSE (0)::double precision
                END AS wax_volume_7_days,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '7 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.usd_price
                    ELSE (0)::double precision
                END AS usd_volume_7_days,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '1 day'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.num_items
                    ELSE 0
                END AS purchases_1_day,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '2 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.num_items
                    ELSE 0
                END AS purchases_2_days,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '3 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.num_items
                    ELSE 0
                END AS purchases_3_days,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '7 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.num_items
                    ELSE 0
                END AS purchases_7_days,
            sales_summary.type,
            sales_summary.collection
           FROM public.sales_summary
          WHERE (sales_summary."timestamp" > ((now() - '7 days'::interval) AT TIME ZONE 'utc'::text))) t
  GROUP BY t.type, t.collection
  ORDER BY (sum(t.wax_volume_1_day)) DESC
  WITH NO DATA;


ALTER TABLE public.collection_volumes_s_mv OWNER TO postgres;

--
-- Name: collection_votes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.collection_votes (
    voter character varying(13),
    collection character varying(13),
    amount double precision,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.collection_votes OWNER TO postgres;

--
-- Name: collections; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.collections (
    collection character varying(13) NOT NULL,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    name_id integer,
    image_id integer,
    author character varying(13),
    url character varying(256),
    description text,
    market_fee double precision,
    authorized character varying(13)[],
    socials text,
    creator_info text,
    images text,
    verified boolean DEFAULT false,
    blacklisted boolean DEFAULT false
);


ALTER TABLE public.collections OWNER TO postgres;

--
-- Name: craft_actions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.craft_actions (
    craft_id integer,
    crafter character varying(13),
    action character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.craft_actions OWNER TO postgres;

--
-- Name: craft_erase_updates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.craft_erase_updates (
    craft_id integer,
    erased boolean,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    applied boolean DEFAULT false
);


ALTER TABLE public.craft_erase_updates OWNER TO postgres;

--
-- Name: craft_erase_updates_reversed; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.craft_erase_updates_reversed (
    craft_id integer,
    erased boolean,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    applied boolean
);


ALTER TABLE public.craft_erase_updates_reversed OWNER TO postgres;

--
-- Name: craft_minting; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.craft_minting (
    craft_id integer,
    result_id bigint,
    crafter character varying(13),
    layer_ingredients json,
    lockups bigint[],
    ipfs character varying(46),
    minted boolean DEFAULT false,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.craft_minting OWNER TO postgres;

--
-- Name: craft_ready_updates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.craft_ready_updates (
    craft_id integer,
    ready boolean,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    applied boolean DEFAULT false
);


ALTER TABLE public.craft_ready_updates OWNER TO postgres;

--
-- Name: craft_ready_updates_reversed; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.craft_ready_updates_reversed (
    craft_id integer,
    ready boolean,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    applied boolean
);


ALTER TABLE public.craft_ready_updates_reversed OWNER TO postgres;

--
-- Name: craft_results; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.craft_results (
    craft_id integer,
    result_id bigint,
    crafter character varying(13),
    result_asset_ids bigint[],
    minted_templates integer[],
    token_results character varying(64)[],
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.craft_results OWNER TO postgres;

--
-- Name: craft_times_updates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.craft_times_updates (
    craft_id integer,
    new_unlock_time timestamp without time zone,
    old_unlock_time timestamp without time zone,
    new_end_time timestamp without time zone,
    old_end_time timestamp without time zone,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    applied boolean
);


ALTER TABLE public.craft_times_updates OWNER TO postgres;

--
-- Name: craft_times_updates_reversed; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.craft_times_updates_reversed (
    craft_id integer,
    new_unlock_time timestamp without time zone,
    old_unlock_time timestamp without time zone,
    new_end_time timestamp without time zone,
    old_end_time timestamp without time zone,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    applied boolean
);


ALTER TABLE public.craft_times_updates_reversed OWNER TO postgres;

--
-- Name: craft_total_updates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.craft_total_updates (
    craft_id integer,
    new_total integer,
    old_total integer,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    applied boolean DEFAULT false
);


ALTER TABLE public.craft_total_updates OWNER TO postgres;

--
-- Name: craft_total_updates_reversed; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.craft_total_updates_reversed (
    craft_id integer,
    new_total integer,
    old_total integer,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    applied boolean
);


ALTER TABLE public.craft_total_updates_reversed OWNER TO postgres;

--
-- Name: craft_updates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.craft_updates (
    craft_id integer,
    new_display_data text,
    old_display_data text,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    applied boolean DEFAULT false
);


ALTER TABLE public.craft_updates OWNER TO postgres;

--
-- Name: crafts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.crafts (
    craft_id integer,
    collection character varying(13),
    contract character varying(13),
    display_data text,
    recipe json,
    outcomes json,
    unlock_time timestamp without time zone,
    num_crafted integer,
    total integer,
    erased boolean,
    ready boolean,
    end_time timestamp without time zone,
    is_hidden boolean DEFAULT false,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.crafts OWNER TO postgres;

--
-- Name: data; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.data (
    data_id integer NOT NULL,
    data text
);


ALTER TABLE public.data OWNER TO postgres;

--
-- Name: data_data_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.data_data_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.data_data_id_seq OWNER TO postgres;

--
-- Name: data_data_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.data_data_id_seq OWNED BY public.data.data_id;


--
-- Name: drop_actions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.drop_actions (
    transaction_id character varying(256),
    seq bigint,
    drop_id bigint,
    claimer character varying(13),
    amount integer,
    "timestamp" timestamp without time zone,
    wax_usd double precision,
    action character varying(13),
    contract character varying(13)
);


ALTER TABLE public.drop_actions OWNER TO postgres;

--
-- Name: drop_auth_updates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.drop_auth_updates (
    drop_id bigint,
    contract character varying(13),
    new_auth_required boolean,
    old_auth_required boolean,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    applied boolean DEFAULT false
);


ALTER TABLE public.drop_auth_updates OWNER TO postgres;

--
-- Name: drop_auth_updates_reversed; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.drop_auth_updates_reversed (
    drop_id bigint,
    contract character varying(12),
    new_auth_required boolean,
    old_auth_required boolean,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    applied boolean
);


ALTER TABLE public.drop_auth_updates_reversed OWNER TO postgres;

--
-- Name: drop_claims; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.drop_claims (
    drop_id bigint,
    contract character varying(13),
    claimer character varying(13),
    country character varying(12),
    referrer character varying(13),
    amount integer,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.drop_claims OWNER TO postgres;

--
-- Name: drop_claim_counts_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.drop_claim_counts_mv AS
 SELECT drop_claims.drop_id,
    drop_claims.contract,
    sum(drop_claims.amount) AS total_claims
   FROM public.drop_claims
  GROUP BY drop_claims.drop_id, drop_claims.contract
  WITH NO DATA;


ALTER TABLE public.drop_claim_counts_mv OWNER TO postgres;

--
-- Name: drop_display_updates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.drop_display_updates (
    drop_id bigint,
    contract character varying(13),
    new_display_data text,
    old_display_data text,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    applied boolean DEFAULT false
);


ALTER TABLE public.drop_display_updates OWNER TO postgres;

--
-- Name: drop_display_updates_reversed; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.drop_display_updates_reversed (
    drop_id bigint,
    contract character varying(13),
    new_display_data text,
    old_display_data text,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    applied boolean
);


ALTER TABLE public.drop_display_updates_reversed OWNER TO postgres;

--
-- Name: drop_erase_updates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.drop_erase_updates (
    drop_id bigint,
    contract character varying(13),
    erased boolean,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    applied boolean DEFAULT false
);


ALTER TABLE public.drop_erase_updates OWNER TO postgres;

--
-- Name: drop_erase_updates_reversed; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.drop_erase_updates_reversed (
    drop_id bigint,
    contract character varying(13),
    erased boolean,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    applied boolean
);


ALTER TABLE public.drop_erase_updates_reversed OWNER TO postgres;

--
-- Name: drop_fee_updates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.drop_fee_updates (
    drop_id bigint,
    contract character varying(13),
    new_fee_rate double precision,
    old_fee_rate double precision,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    applied boolean DEFAULT false
);


ALTER TABLE public.drop_fee_updates OWNER TO postgres;

--
-- Name: drop_fee_updates_reversed; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.drop_fee_updates_reversed (
    drop_id bigint,
    contract character varying(13),
    new_fee_rate double precision,
    old_fee_rate double precision,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    applied boolean
);


ALTER TABLE public.drop_fee_updates_reversed OWNER TO postgres;

--
-- Name: drop_hidden_updates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.drop_hidden_updates (
    drop_id bigint,
    contract character varying(13),
    new_is_hidden boolean,
    old_is_hidden boolean,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    applied boolean DEFAULT false
);


ALTER TABLE public.drop_hidden_updates OWNER TO postgres;

--
-- Name: drop_hidden_updates_reversed; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.drop_hidden_updates_reversed (
    drop_id bigint,
    contract character varying(13),
    new_is_hidden boolean,
    old_is_hidden boolean,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    applied boolean
);


ALTER TABLE public.drop_hidden_updates_reversed OWNER TO postgres;

--
-- Name: drop_limit_updates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.drop_limit_updates (
    drop_id bigint,
    contract character varying(13),
    new_account_limit integer,
    new_account_limit_cooldown bigint,
    old_account_limit integer,
    old_account_limit_cooldown bigint,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    applied boolean DEFAULT false
);


ALTER TABLE public.drop_limit_updates OWNER TO postgres;

--
-- Name: drop_limit_updates_reversed; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.drop_limit_updates_reversed (
    drop_id bigint,
    contract character varying(13),
    new_account_limit integer,
    new_account_limit_cooldown bigint,
    old_account_limit integer,
    old_account_limit_cooldown bigint,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    applied boolean
);


ALTER TABLE public.drop_limit_updates_reversed OWNER TO postgres;

--
-- Name: drop_log_prices; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.drop_log_prices (
    drop_id integer,
    contract character varying(13),
    prices json,
    currencies character varying(12)[],
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.drop_log_prices OWNER TO postgres;

--
-- Name: drop_max_updates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.drop_max_updates (
    drop_id bigint,
    contract character varying(13),
    new_max_claimable bigint,
    old_max_claimable bigint,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    applied boolean DEFAULT false
);


ALTER TABLE public.drop_max_updates OWNER TO postgres;

--
-- Name: drop_max_updates_reversed; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.drop_max_updates_reversed (
    drop_id bigint,
    contract character varying(13),
    new_max_claimable bigint,
    old_max_claimable bigint,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    applied boolean
);


ALTER TABLE public.drop_max_updates_reversed OWNER TO postgres;

--
-- Name: drop_price_updates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.drop_price_updates (
    drop_id bigint,
    contract character varying(13),
    new_price double precision,
    new_currency character varying(12),
    old_price double precision,
    old_currency character varying(12),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    applied boolean DEFAULT false
);


ALTER TABLE public.drop_price_updates OWNER TO postgres;

--
-- Name: drop_price_updates_reversed; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.drop_price_updates_reversed (
    drop_id bigint,
    contract character varying(13),
    new_price double precision,
    new_currency character varying(12),
    old_price double precision,
    old_currency character varying(12),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    applied boolean
);


ALTER TABLE public.drop_price_updates_reversed OWNER TO postgres;

--
-- Name: drop_prices_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.drop_prices_mv AS
 SELECT lp.drop_id,
    lp.contract,
    lp.prices,
    lp.currencies
   FROM public.drop_log_prices lp
  WHERE (lp.seq = ( SELECT max(drop_log_prices.seq) AS max
           FROM public.drop_log_prices
          WHERE ((drop_log_prices.drop_id = lp.drop_id) AND ((drop_log_prices.contract)::text = (lp.contract)::text))))
  WITH NO DATA;


ALTER TABLE public.drop_prices_mv OWNER TO postgres;

--
-- Name: drop_times_updates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.drop_times_updates (
    drop_id bigint,
    contract character varying(13),
    new_start_time timestamp without time zone,
    new_end_time timestamp without time zone,
    old_start_time timestamp without time zone,
    old_end_time timestamp without time zone,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    applied boolean DEFAULT false
);


ALTER TABLE public.drop_times_updates OWNER TO postgres;

--
-- Name: drop_times_updates_reversed; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.drop_times_updates_reversed (
    drop_id bigint,
    contract character varying(13),
    new_start_time timestamp without time zone,
    new_end_time timestamp without time zone,
    old_start_time timestamp without time zone,
    old_end_time timestamp without time zone,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    applied boolean
);


ALTER TABLE public.drop_times_updates_reversed OWNER TO postgres;

--
-- Name: drop_token_actions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.drop_token_actions (
    contract character varying(13),
    symbol character varying(13),
    decimals integer,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    action character varying(13)
);


ALTER TABLE public.drop_token_actions OWNER TO postgres;

--
-- Name: drops; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.drops (
    drop_id bigint,
    contract character varying(13),
    collection character varying(13),
    price double precision,
    currency character varying(12),
    fee double precision,
    display_data text,
    start_time timestamp without time zone,
    end_time timestamp without time zone,
    max_claimable bigint,
    num_claimed bigint,
    erased boolean DEFAULT false,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    account_limit integer,
    account_limit_cooldown bigint,
    posted boolean,
    templates_to_mint bigint[],
    auth_required boolean DEFAULT false,
    is_hidden boolean DEFAULT false
);


ALTER TABLE public.drops OWNER TO postgres;

--
-- Name: drops_summary; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.drops_summary (
    collection character varying(13),
    type text,
    price double precision,
    usd_price double precision,
    num_items integer,
    buyer character varying(13),
    seller character varying(13),
    market character varying(13),
    maker text,
    taker text,
    drop_id bigint,
    "timestamp" timestamp without time zone,
    seq bigint,
    block_num bigint
);


ALTER TABLE public.drops_summary OWNER TO postgres;

--
-- Name: duplicate_atomic_listings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.duplicate_atomic_listings (
    asset_ids bigint[],
    seller character varying(13),
    price double precision,
    currency character varying(12),
    listing_id bigint,
    maker character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.duplicate_atomic_listings OWNER TO postgres;

--
-- Name: error_transactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.error_transactions (
    transaction_id integer,
    seq bigint,
    "timestamp" timestamp without time zone,
    block_num bigint,
    account character varying(13),
    action_name character varying(13),
    data json,
    transaction_type integer,
    ingested boolean,
    actor character varying(13)
);


ALTER TABLE public.error_transactions OWNER TO postgres;

--
-- Name: favorites; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.favorites (
    user_name character varying(13),
    asset_id bigint,
    template_id integer,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.favorites OWNER TO postgres;

--
-- Name: floor_prices_by_date; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.floor_prices_by_date (
    template_id integer,
    collection character varying(13),
    floor_date timestamp without time zone,
    floor double precision
);


ALTER TABLE public.floor_prices_by_date OWNER TO postgres;

--
-- Name: floor_price_change_24h_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.floor_price_change_24h_mv AS
 SELECT fp.template_id,
    fp.collection,
    fp.floor,
    fp2.floor AS floor_prev,
    (fp.floor - fp2.floor) AS change
   FROM (public.floor_prices_by_date fp
     LEFT JOIN public.floor_prices_by_date fp2 ON (((fp2.template_id = fp.template_id) AND (fp2.floor_date = (fp.floor_date - '1 day'::interval)))))
  WHERE (fp.floor_date = ( SELECT max(floor_prices_by_date.floor_date) AS max
           FROM public.floor_prices_by_date
          WHERE (floor_prices_by_date.template_id = fp.template_id)))
  WITH NO DATA;


ALTER TABLE public.floor_price_change_24h_mv OWNER TO postgres;

--
-- Name: floor_prices_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.floor_prices_mv AS
 SELECT l.collection,
    a.schema,
    a.template_id,
    min(l.estimated_wax_price) AS floor_price
   FROM (public.listings l
     JOIN public.assets a ON ((a.asset_id = l.asset_ids[1])))
  WHERE (a.template_id > 0)
  GROUP BY l.collection, a.schema, a.template_id
  WITH NO DATA;


ALTER TABLE public.floor_prices_mv OWNER TO postgres;

--
-- Name: floor_template_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.floor_template_mv AS
 SELECT s.collection,
    t.template_id,
    min(s.estimated_wax_price) AS floor_wax
   FROM ((public.listings s
     JOIN public.assets a ON ((a.asset_id = s.asset_ids[1])))
     JOIN public.templates t USING (template_id))
  WHERE (t.template_id > 0)
  GROUP BY s.collection, t.template_id
  WITH NO DATA;


ALTER TABLE public.floor_template_mv OWNER TO postgres;

--
-- Name: follows; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.follows (
    user_name character varying(13),
    collection character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.follows OWNER TO postgres;

--
-- Name: forks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.forks (
    block_num bigint,
    unconfirmed_block bigint,
    confirmed_block bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.forks OWNER TO postgres;

--
-- Name: ft_listings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ft_listings (
    symbol character varying(12),
    contract character varying(12),
    order_id integer,
    market character varying(12),
    price double precision,
    currency character varying(12),
    amount integer,
    seller character varying(12),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    active boolean DEFAULT false
);


ALTER TABLE public.ft_listings OWNER TO postgres;

--
-- Name: handle_fork; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.handle_fork (
    forked boolean,
    block_num bigint
);


ALTER TABLE public.handle_fork OWNER TO postgres;

--
-- Name: images; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.images (
    image_id integer NOT NULL,
    image character varying(256)
);


ALTER TABLE public.images OWNER TO postgres;

--
-- Name: images_image_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.images_image_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.images_image_id_seq OWNER TO postgres;

--
-- Name: images_image_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.images_image_id_seq OWNED BY public.images.image_id;


--
-- Name: listings_floor_breakdown_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.listings_floor_breakdown_mv AS
 SELECT a.collection,
    a.schema,
    a.template_id,
    att.attribute_id,
    min(l.estimated_wax_price) AS floor_price
   FROM ((public.listings l
     LEFT JOIN public.assets a ON ((a.asset_id = ANY (l.asset_ids))))
     LEFT JOIN public.attributes att ON ((att.attribute_id = ANY (a.attribute_ids))))
  GROUP BY a.collection, a.schema, a.template_id, att.attribute_id
  WITH NO DATA;


ALTER TABLE public.listings_floor_breakdown_mv OWNER TO postgres;

--
-- Name: names; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.names (
    name_id integer NOT NULL,
    name character varying(256)
);


ALTER TABLE public.names OWNER TO postgres;

--
-- Name: pfp_assets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pfp_assets (
    asset_id bigint NOT NULL,
    collection character varying(13),
    schema character varying(13),
    template_id integer,
    attribute_ids integer[],
    rarity_score double precision,
    rank integer,
    num_traits integer
);


ALTER TABLE public.pfp_assets OWNER TO postgres;

--
-- Name: template_floor_prices_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.template_floor_prices_mv AS
 SELECT listings_floor_breakdown_mv.collection,
    listings_floor_breakdown_mv.schema,
    listings_floor_breakdown_mv.template_id,
    min(listings_floor_breakdown_mv.floor_price) AS floor_price
   FROM public.listings_floor_breakdown_mv
  WHERE (listings_floor_breakdown_mv.template_id > 1)
  GROUP BY listings_floor_breakdown_mv.collection, listings_floor_breakdown_mv.schema, listings_floor_breakdown_mv.template_id
  WITH NO DATA;


ALTER TABLE public.template_floor_prices_mv OWNER TO postgres;

--
-- Name: listings_helper_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.listings_helper_mv AS
 SELECT l.sale_id,
    a.mint,
    n.name,
    p.rarity_score,
    p.rank,
    a.template_id,
    a.schema,
    f.floor_price
   FROM ((((public.listings l
     JOIN public.assets a ON ((a.asset_id = l.asset_ids[1])))
     LEFT JOIN public.names n USING (name_id))
     LEFT JOIN public.pfp_assets p USING (asset_id))
     LEFT JOIN public.template_floor_prices_mv f ON ((f.template_id = a.template_id)))
  WITH NO DATA;


ALTER TABLE public.listings_helper_mv OWNER TO postgres;

--
-- Name: listings_sale_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.listings_sale_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.listings_sale_id_seq OWNER TO postgres;

--
-- Name: listings_sale_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.listings_sale_id_seq OWNED BY public.listings.sale_id;


--
-- Name: market_actions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.market_actions (
    sale_id integer,
    market character varying(13),
    actor character varying(13),
    action character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.market_actions OWNER TO postgres;

--
-- Name: market_collection_volumes_14_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.market_collection_volumes_14_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    count(1) AS sales,
    t.collection,
    t.market,
    t.maker,
    t.taker,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '14 days'::interval))
  GROUP BY t.collection, t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.market_collection_volumes_14_mv OWNER TO postgres;

--
-- Name: market_collection_volumes_15_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.market_collection_volumes_15_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    count(1) AS sales,
    t.collection,
    t.market,
    t.maker,
    t.taker,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '15 days'::interval))
  GROUP BY t.collection, t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.market_collection_volumes_15_mv OWNER TO postgres;

--
-- Name: market_collection_volumes_180_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.market_collection_volumes_180_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    count(1) AS sales,
    t.collection,
    t.market,
    t.maker,
    t.taker,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '180 days'::interval))
  GROUP BY t.collection, t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.market_collection_volumes_180_mv OWNER TO postgres;

--
-- Name: market_collection_volumes_1_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.market_collection_volumes_1_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    count(1) AS sales,
    t.collection,
    t.market,
    t.maker,
    t.taker,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '1 day'::interval))
  GROUP BY t.collection, t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.market_collection_volumes_1_mv OWNER TO postgres;

--
-- Name: market_collection_volumes_2_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.market_collection_volumes_2_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    count(1) AS sales,
    t.collection,
    t.market,
    t.maker,
    t.taker,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '2 days'::interval))
  GROUP BY t.collection, t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.market_collection_volumes_2_mv OWNER TO postgres;

--
-- Name: market_collection_volumes_30_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.market_collection_volumes_30_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    count(1) AS sales,
    t.collection,
    t.market,
    t.maker,
    t.taker,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '30 days'::interval))
  GROUP BY t.collection, t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.market_collection_volumes_30_mv OWNER TO postgres;

--
-- Name: market_collection_volumes_365_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.market_collection_volumes_365_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    count(1) AS sales,
    t.collection,
    t.market,
    t.maker,
    t.taker,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '365 days'::interval))
  GROUP BY t.collection, t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.market_collection_volumes_365_mv OWNER TO postgres;

--
-- Name: market_collection_volumes_3_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.market_collection_volumes_3_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    count(1) AS sales,
    t.collection,
    t.market,
    t.maker,
    t.taker,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '3 days'::interval))
  GROUP BY t.collection, t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.market_collection_volumes_3_mv OWNER TO postgres;

--
-- Name: market_collection_volumes_60_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.market_collection_volumes_60_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    count(1) AS sales,
    t.collection,
    t.market,
    t.maker,
    t.taker,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '60 days'::interval))
  GROUP BY t.collection, t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.market_collection_volumes_60_mv OWNER TO postgres;

--
-- Name: market_collection_volumes_7_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.market_collection_volumes_7_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    count(1) AS sales,
    t.collection,
    t.market,
    t.maker,
    t.taker,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '7 days'::interval))
  GROUP BY t.collection, t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.market_collection_volumes_7_mv OWNER TO postgres;

--
-- Name: market_collection_volumes_90_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.market_collection_volumes_90_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    count(1) AS sales,
    t.collection,
    t.market,
    t.maker,
    t.taker,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '90 days'::interval))
  GROUP BY t.collection, t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.market_collection_volumes_90_mv OWNER TO postgres;

--
-- Name: market_collection_volumes_from_2023_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.market_collection_volumes_from_2023_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales,
    t.collection,
    t.market,
    t.maker,
    t.taker,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > '2023-01-01 00:00:00'::timestamp without time zone)
  GROUP BY t.collection, t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.market_collection_volumes_from_2023_mv OWNER TO postgres;

--
-- Name: market_myth_sales; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.market_myth_sales (
    asset_ids bigint[],
    seller character varying(13),
    buyer character varying(13),
    price double precision,
    currency character varying(12),
    listing_id bigint,
    market character varying(13),
    maker character varying(13),
    taker character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    wax_price double precision
);


ALTER TABLE public.market_myth_sales OWNER TO postgres;

--
-- Name: market_statuses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.market_statuses (
    market character varying(13),
    list_name character varying(13),
    collection character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.market_statuses OWNER TO postgres;

--
-- Name: market_volumes_14_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.market_volumes_14_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    count(1) AS sales,
    t.market,
    t.maker,
    t.taker,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '14 days'::interval))
  GROUP BY t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.market_volumes_14_mv OWNER TO postgres;

--
-- Name: market_volumes_15_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.market_volumes_15_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    count(1) AS sales,
    t.market,
    t.maker,
    t.taker,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '15 days'::interval))
  GROUP BY t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.market_volumes_15_mv OWNER TO postgres;

--
-- Name: market_volumes_180_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.market_volumes_180_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    count(1) AS sales,
    t.market,
    t.maker,
    t.taker,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '180 days'::interval))
  GROUP BY t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.market_volumes_180_mv OWNER TO postgres;

--
-- Name: market_volumes_1_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.market_volumes_1_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    count(1) AS sales,
    t.market,
    t.maker,
    t.taker,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '1 day'::interval))
  GROUP BY t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.market_volumes_1_mv OWNER TO postgres;

--
-- Name: market_volumes_2_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.market_volumes_2_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    count(1) AS sales,
    t.market,
    t.maker,
    t.taker,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '2 days'::interval))
  GROUP BY t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.market_volumes_2_mv OWNER TO postgres;

--
-- Name: market_volumes_30_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.market_volumes_30_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    count(1) AS sales,
    t.market,
    t.maker,
    t.taker,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '30 days'::interval))
  GROUP BY t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.market_volumes_30_mv OWNER TO postgres;

--
-- Name: market_volumes_365_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.market_volumes_365_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    count(1) AS sales,
    t.market,
    t.maker,
    t.taker,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '365 days'::interval))
  GROUP BY t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.market_volumes_365_mv OWNER TO postgres;

--
-- Name: market_volumes_3_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.market_volumes_3_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    count(1) AS sales,
    t.market,
    t.maker,
    t.taker,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '3 days'::interval))
  GROUP BY t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.market_volumes_3_mv OWNER TO postgres;

--
-- Name: market_volumes_4_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.market_volumes_4_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    count(1) AS sales,
    t.market,
    t.maker,
    t.taker,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '4 days'::interval))
  GROUP BY t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.market_volumes_4_mv OWNER TO postgres;

--
-- Name: market_volumes_60_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.market_volumes_60_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    count(1) AS sales,
    t.market,
    t.maker,
    t.taker,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '60 days'::interval))
  GROUP BY t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.market_volumes_60_mv OWNER TO postgres;

--
-- Name: market_volumes_7_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.market_volumes_7_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    count(1) AS sales,
    t.market,
    t.maker,
    t.taker,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '7 days'::interval))
  GROUP BY t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.market_volumes_7_mv OWNER TO postgres;

--
-- Name: market_volumes_90_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.market_volumes_90_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(DISTINCT t.buyer) AS buyers,
    count(DISTINCT t.seller) AS sellers,
    count(1) AS sales,
    t.market,
    t.maker,
    t.taker,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '90 days'::interval))
  GROUP BY t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.market_volumes_90_mv OWNER TO postgres;

--
-- Name: market_volumes_from_2023_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.market_volumes_from_2023_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales,
    t.market,
    t.maker,
    t.taker,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > '2023-01-01 00:00:00'::timestamp without time zone)
  GROUP BY t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.market_volumes_from_2023_mv OWNER TO postgres;

--
-- Name: memos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.memos (
    memo_id integer NOT NULL,
    memo text
);


ALTER TABLE public.memos OWNER TO postgres;

--
-- Name: memos_memo_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.memos_memo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.memos_memo_id_seq OWNER TO postgres;

--
-- Name: memos_memo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.memos_memo_id_seq OWNED BY public.memos.memo_id;


--
-- Name: mirror_mints; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mirror_mints (
    result_id character varying(48) NOT NULL,
    ipfs character varying(46),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.mirror_mints OWNER TO postgres;

--
-- Name: mirror_results; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mirror_results (
    craft_id integer,
    result_id bigint,
    crafter character varying(13),
    minted_template integer,
    mirror_result json,
    minted boolean,
    ipfs character varying(46),
    error boolean,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.mirror_results OWNER TO postgres;

--
-- Name: mirror_swap_mints; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mirror_swap_mints (
    result_id character varying(48) NOT NULL,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.mirror_swap_mints OWNER TO postgres;

--
-- Name: mirror_swap_results; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mirror_swap_results (
    craft_id bigint,
    claimer character varying(13),
    results text,
    ipfs character varying(46),
    result_id character varying(48),
    minted boolean DEFAULT false,
    external boolean DEFAULT false,
    error boolean DEFAULT false,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.mirror_swap_results OWNER TO postgres;

--
-- Name: monthly_collection_volume_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.monthly_collection_volume_mv AS
 SELECT to_date(to_char((collection_sales_by_date_mv.to_date)::timestamp with time zone, 'YYYY-MM'::text), 'YYYY-MM'::text) AS to_date,
    collection_sales_by_date_mv.collection,
    collection_sales_by_date_mv.type,
    sum(collection_sales_by_date_mv.wax_volume) AS wax_volume,
    sum(collection_sales_by_date_mv.usd_volume) AS usd_volume
   FROM public.collection_sales_by_date_mv
  GROUP BY (to_date(to_char((collection_sales_by_date_mv.to_date)::timestamp with time zone, 'YYYY-MM'::text), 'YYYY-MM'::text)), collection_sales_by_date_mv.collection, collection_sales_by_date_mv.type
  WITH NO DATA;


ALTER TABLE public.monthly_collection_volume_mv OWNER TO postgres;

--
-- Name: names_name_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.names_name_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.names_name_id_seq OWNER TO postgres;

--
-- Name: names_name_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.names_name_id_seq OWNED BY public.names.name_id;


--
-- Name: nft_hive_actions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.nft_hive_actions (
    account character varying(13),
    seq bigint,
    "timestamp" timestamp without time zone,
    order_id integer,
    action character varying(13)
);


ALTER TABLE public.nft_hive_actions OWNER TO postgres;

--
-- Name: notification_users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notification_users (
    user_name character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.notification_users OWNER TO postgres;

--
-- Name: notifications; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notifications (
    user_name character varying(13),
    type text,
    transaction_id character varying(256),
    asset_id bigint,
    read boolean,
    "timestamp" timestamp without time zone,
    price double precision,
    bundle boolean,
    market character varying(13),
    seq bigint,
    offer_id bigint
);


ALTER TABLE public.notifications OWNER TO postgres;

--
-- Name: pack_announcements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pack_announcements (
    contract character varying(13),
    collection character varying(13),
    display_data text,
    unlock_time timestamp without time zone,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.pack_announcements OWNER TO postgres;

--
-- Name: pack_creations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pack_creations (
    contract character varying(13),
    collection character varying(13),
    display_data text,
    unlock_time timestamp without time zone,
    template_id integer,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.pack_creations OWNER TO postgres;

--
-- Name: pack_display_updates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pack_display_updates (
    pack_id integer,
    contract character varying(13),
    old_display_data text,
    new_display_data text,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.pack_display_updates OWNER TO postgres;

--
-- Name: pack_template_updates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pack_template_updates (
    pack_id integer,
    contract character varying(13),
    old_template_id integer,
    new_template_id integer,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.pack_template_updates OWNER TO postgres;

--
-- Name: pack_time_updates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pack_time_updates (
    pack_id integer,
    contract character varying(13),
    old_unlock_time timestamp without time zone,
    new_unlock_time timestamp without time zone,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.pack_time_updates OWNER TO postgres;

--
-- Name: pack_updates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pack_updates (
    pack_id integer,
    contract character varying(13),
    unlock_time timestamp without time zone,
    seq bigint,
    "timestamp" timestamp without time zone,
    display_data text,
    template_id integer,
    block_num bigint,
    collection character varying(13)
);


ALTER TABLE public.pack_updates OWNER TO postgres;

--
-- Name: packs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.packs (
    pack_id integer,
    contract character varying(13),
    collection character varying(13),
    unlock_time timestamp without time zone,
    display_data text,
    template_id integer,
    unpack_url character varying(256),
    release_id integer,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.packs OWNER TO postgres;

--
-- Name: personal_blacklist_actions_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.personal_blacklist_actions_mv AS
 SELECT account_value_actions.seq,
    account_value_actions.account,
    account_value_actions.action_name,
    unnest(account_value_actions."values") AS collection
   FROM public.account_value_actions
  WHERE (((account_value_actions.list_name)::text = 'col.blist'::text) AND ((account_value_actions.account)::text <> 'atomhubtools'::text))
  WITH NO DATA;


ALTER TABLE public.personal_blacklist_actions_mv OWNER TO postgres;

--
-- Name: personal_blacklist_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.personal_blacklist_mv AS
 SELECT pb.account,
    pb.collection
   FROM public.personal_blacklist_actions_mv pb
  WHERE (((pb.action_name)::text = 'addaccvalues'::text) AND (pb.seq = ( SELECT max(personal_blacklist_actions_mv.seq) AS max
           FROM public.personal_blacklist_actions_mv
          WHERE (((personal_blacklist_actions_mv.account)::text = (pb.account)::text) AND ((personal_blacklist_actions_mv.collection)::text = (pb.collection)::text)))))
  WITH NO DATA;


ALTER TABLE public.personal_blacklist_mv OWNER TO postgres;

--
-- Name: pfp_attribute_blacklist; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pfp_attribute_blacklist (
    attribute_name character varying(32)
);


ALTER TABLE public.pfp_attribute_blacklist OWNER TO postgres;

--
-- Name: pfp_drop_data; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pfp_drop_data (
    drop_id bigint,
    contract character varying(13),
    attributes json,
    name_pattern character varying(120)
);


ALTER TABLE public.pfp_drop_data OWNER TO postgres;

--
-- Name: pfp_mints; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pfp_mints (
    result_id character varying(48),
    drop_id bigint,
    owner character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.pfp_mints OWNER TO postgres;

--
-- Name: pfp_results; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pfp_results (
    drop_id bigint,
    claimer character varying(13),
    results text,
    ipfs character varying(46),
    result_id character varying(48),
    minted boolean,
    external boolean,
    error boolean,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    name character varying(64)
);


ALTER TABLE public.pfp_results OWNER TO postgres;

--
-- Name: pfp_schemas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pfp_schemas (
    collection character varying(13),
    schema character varying(13)
);


ALTER TABLE public.pfp_schemas OWNER TO postgres;

--
-- Name: pfp_swap_mints; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pfp_swap_mints (
    result_id character varying(48),
    drop_id bigint,
    asset_id bigint,
    owner character varying(13),
    hash character varying(46),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.pfp_swap_mints OWNER TO postgres;

--
-- Name: pfp_swap_results; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pfp_swap_results (
    drop_id bigint,
    claimer character varying(12),
    result text,
    ipfs character varying(46),
    result_id character varying(48),
    minted boolean DEFAULT false,
    external boolean DEFAULT false,
    error boolean DEFAULT false,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.pfp_swap_results OWNER TO postgres;

--
-- Name: pfp_templates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pfp_templates (
    collection character varying(13),
    schema character varying(13),
    template_id integer
);


ALTER TABLE public.pfp_templates OWNER TO postgres;

--
-- Name: pool_assets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pool_assets (
    pool_id bigint,
    contract character varying(13),
    asset_id bigint,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.pool_assets OWNER TO postgres;

--
-- Name: pool_deletions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pool_deletions (
    pool_id bigint,
    contract character varying(13),
    asset_id bigint,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.pool_deletions OWNER TO postgres;

--
-- Name: pools; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pools (
    pool_id integer,
    contract character varying(13),
    release_id integer,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.pools OWNER TO postgres;

--
-- Name: purchased_atomic_listings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.purchased_atomic_listings (
    asset_ids bigint[],
    collection character varying(13),
    seller character varying(13),
    market character varying(13),
    maker character varying(13),
    price double precision,
    currency character varying(12),
    listing_id bigint,
    sale_id bigint,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    estimated_wax_price double precision
);


ALTER TABLE public.purchased_atomic_listings OWNER TO postgres;

--
-- Name: recently_sold_day_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.recently_sold_day_mv AS
 SELECT DISTINCT template_sales.template_id
   FROM public.template_sales
  WHERE (template_sales."timestamp" > (now() - '1 day'::interval))
  WITH NO DATA;


ALTER TABLE public.recently_sold_day_mv OWNER TO postgres;

--
-- Name: recently_sold_hour_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.recently_sold_hour_mv AS
 SELECT DISTINCT template_sales.template_id
   FROM public.template_sales
  WHERE (template_sales."timestamp" > (now() - '01:00:00'::interval))
  WITH NO DATA;


ALTER TABLE public.recently_sold_hour_mv OWNER TO postgres;

--
-- Name: recently_sold_month_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.recently_sold_month_mv AS
 SELECT DISTINCT template_sales.template_id
   FROM public.template_sales
  WHERE (template_sales."timestamp" > (now() - '1 mon'::interval))
  WITH NO DATA;


ALTER TABLE public.recently_sold_month_mv OWNER TO postgres;

--
-- Name: recently_sold_week_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.recently_sold_week_mv AS
 SELECT DISTINCT template_sales.template_id
   FROM public.template_sales
  WHERE (template_sales."timestamp" > (now() - '7 days'::interval))
  WITH NO DATA;


ALTER TABLE public.recently_sold_week_mv OWNER TO postgres;

--
-- Name: redeem_actions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.redeem_actions (
    asset_owner character varying(13),
    authorized_account character varying(13),
    asset_id bigint,
    action character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    memo_id integer
);


ALTER TABLE public.redeem_actions OWNER TO postgres;

--
-- Name: redeem_rejections; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.redeem_rejections (
    authorized_account character varying(13),
    asset_id bigint,
    memo_id integer,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.redeem_rejections OWNER TO postgres;

--
-- Name: redeem_user_actions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.redeem_user_actions (
    asset_owner character varying(13),
    asset_id bigint,
    action character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.redeem_user_actions OWNER TO postgres;

--
-- Name: redemptions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.redemptions (
    redeemer character varying(13),
    asset_id bigint,
    status character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    transaction_id integer
);


ALTER TABLE public.redemptions OWNER TO postgres;

--
-- Name: removed_atomic_listings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.removed_atomic_listings (
    asset_ids bigint[],
    collection character varying(13),
    seller character varying(13),
    market character varying(13),
    maker character varying(13),
    price double precision,
    currency character varying(12),
    listing_id bigint,
    sale_id bigint,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    estimated_wax_price double precision,
    removed_seq bigint,
    removed_block_num bigint
);


ALTER TABLE public.removed_atomic_listings OWNER TO postgres;

--
-- Name: removed_atomicassets_offers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.removed_atomicassets_offers (
    offer_id bigint,
    sender character varying(13),
    recipient character varying(13),
    sender_asset_ids bigint[],
    recipient_asset_ids bigint[],
    status character varying(12),
    memo_id integer,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    removed_seq bigint,
    removed_block_num bigint
);


ALTER TABLE public.removed_atomicassets_offers OWNER TO postgres;

--
-- Name: removed_atomicmarket_auctions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.removed_atomicmarket_auctions (
    auction_id bigint,
    asset_ids bigint[],
    seller character varying(13),
    end_time timestamp without time zone,
    start_bid double precision,
    current_bid double precision,
    currency character varying(12),
    maker character varying(13),
    market character varying(13),
    active boolean,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    removed_seq bigint,
    removed_block_num bigint
);


ALTER TABLE public.removed_atomicmarket_auctions OWNER TO postgres;

--
-- Name: removed_atomicmarket_buy_offers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.removed_atomicmarket_buy_offers (
    buyoffer_id bigint,
    buyer character varying(13),
    recipient character varying(13),
    price double precision,
    currency character varying(12),
    asset_ids bigint[],
    memo_id integer,
    maker_marketplace character varying(13),
    collection character varying(13),
    collection_fee double precision,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    removed_seq bigint,
    removed_block_num bigint
);


ALTER TABLE public.removed_atomicmarket_buy_offers OWNER TO postgres;

--
-- Name: removed_atomicmarket_template_buy_offers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.removed_atomicmarket_template_buy_offers (
    buyoffer_id bigint,
    buyer character varying(13),
    price double precision,
    currency character varying(12),
    template_id bigint,
    maker character varying(13),
    collection character varying(13),
    collection_fee double precision,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    removed_seq bigint,
    removed_block_num bigint
);


ALTER TABLE public.removed_atomicmarket_template_buy_offers OWNER TO postgres;

--
-- Name: removed_favorites; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.removed_favorites (
    user_name character varying(13),
    asset_id bigint,
    template_id integer,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    removed_seq bigint,
    removed_block_num bigint
);


ALTER TABLE public.removed_favorites OWNER TO postgres;

--
-- Name: removed_follows; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.removed_follows (
    user_name character varying(13),
    collection character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    removed_seq bigint,
    removed_block_num bigint
);


ALTER TABLE public.removed_follows OWNER TO postgres;

--
-- Name: removed_notification_users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.removed_notification_users (
    user_name character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    removed_seq bigint,
    removed_block_num bigint
);


ALTER TABLE public.removed_notification_users OWNER TO postgres;

--
-- Name: removed_pool_assets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.removed_pool_assets (
    pool_id bigint,
    contract character varying(13),
    asset_id bigint,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    removed_seq bigint,
    removed_block_num bigint
);


ALTER TABLE public.removed_pool_assets OWNER TO postgres;

--
-- Name: removed_pools; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.removed_pools (
    pool_id integer,
    contract character varying(13),
    release_id integer,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    removed_seq bigint,
    removed_block_num bigint
);


ALTER TABLE public.removed_pools OWNER TO postgres;

--
-- Name: removed_rwax_tokenizations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.removed_rwax_tokenizations (
    asset_id bigint,
    tokenizer character varying(13),
    symbol character varying(12),
    contract character varying(13),
    amount double precision,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    removed_seq bigint,
    removed_block_num bigint
);


ALTER TABLE public.removed_rwax_tokenizations OWNER TO postgres;

--
-- Name: removed_rwax_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.removed_rwax_tokens (
    collection character varying(13),
    symbol character varying(12),
    contract character varying(13),
    decimals integer,
    maximum_supply double precision,
    template_ids integer[],
    templates_supply json,
    trait_factors json,
    token_name character varying(64),
    token_logo character varying(256),
    token_logo_lg character varying(256),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    removed_seq bigint,
    removed_block_num bigint
);


ALTER TABLE public.removed_rwax_tokens OWNER TO postgres;

--
-- Name: removed_simplemarket_listings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.removed_simplemarket_listings (
    asset_ids bigint[],
    collection character varying(13),
    seller character varying(13),
    market character varying(13),
    maker character varying(13),
    price double precision,
    currency character varying(12),
    listing_id bigint,
    sale_id bigint,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    estimated_wax_price double precision,
    removed_seq bigint,
    removed_block_num bigint
);


ALTER TABLE public.removed_simplemarket_listings OWNER TO postgres;

--
-- Name: removed_stakes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.removed_stakes (
    asset_id bigint,
    stake_contract character varying(13),
    staker character varying(13),
    memo character varying(256),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    removed_seq bigint,
    removed_block_num bigint
);


ALTER TABLE public.removed_stakes OWNER TO postgres;

--
-- Name: removed_waxplorercom_listings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.removed_waxplorercom_listings (
    asset_ids bigint[],
    collection character varying(13),
    seller character varying(13),
    market character varying(13),
    maker character varying(13),
    price double precision,
    currency character varying(12),
    listing_id bigint,
    sale_id bigint,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    estimated_wax_price double precision,
    removed_seq bigint,
    removed_block_num bigint
);


ALTER TABLE public.removed_waxplorercom_listings OWNER TO postgres;

--
-- Name: removed_wuffi_airdrops; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.removed_wuffi_airdrops (
    airdrop_id bigint,
    token character varying(64),
    contract character varying(13),
    creator character varying(13),
    holder_contract character varying(13),
    min_amount character varying(64),
    max_amount character varying(64),
    snapshot_time timestamp without time zone,
    display_data text,
    ready boolean,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    removed_seq bigint,
    removed_block_num bigint
);


ALTER TABLE public.removed_wuffi_airdrops OWNER TO postgres;

--
-- Name: rwax_assets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rwax_assets (
    asset_id bigint NOT NULL,
    collection character varying(13),
    schema character varying(13),
    template_id integer
);


ALTER TABLE public.rwax_assets OWNER TO postgres;

--
-- Name: rwax_erase_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rwax_erase_tokens (
    contract character varying(13),
    decimals integer,
    symbol character varying(12),
    "timestamp" timestamp without time zone,
    seq bigint,
    block_num bigint
);


ALTER TABLE public.rwax_erase_tokens OWNER TO postgres;

--
-- Name: rwax_redemptions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rwax_redemptions (
    asset_id bigint,
    redeemer character varying(13),
    contract character varying(13),
    symbol character varying(12),
    amount double precision,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.rwax_redemptions OWNER TO postgres;

--
-- Name: rwax_templates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rwax_templates (
    template_id integer NOT NULL,
    collection character varying(13),
    decimals integer,
    symbol character varying(12),
    contract character varying(13),
    max_assets integer,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.rwax_templates OWNER TO postgres;

--
-- Name: rwax_tokenizations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rwax_tokenizations (
    asset_id bigint,
    tokenizer character varying(13),
    symbol character varying(12),
    contract character varying(13),
    amount double precision,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.rwax_tokenizations OWNER TO postgres;

--
-- Name: rwax_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rwax_tokens (
    collection character varying(13),
    symbol character varying(12),
    contract character varying(13),
    decimals integer,
    maximum_supply double precision,
    template_ids integer[],
    templates_supply json,
    trait_factors json,
    token_name character varying(64),
    token_logo character varying(256),
    token_logo_lg character varying(256),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.rwax_tokens OWNER TO postgres;

--
-- Name: sales_seven_day_chart_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.sales_seven_day_chart_mv AS
 SELECT sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '1 day'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
            ELSE (0)::double precision
        END) AS wax_volume_day_7,
    sum(
        CASE
            WHEN ((sales_summary."timestamp" >= ((now() - '2 days'::interval) AT TIME ZONE 'utc'::text)) AND (sales_summary."timestamp" <= ((now() - '1 day'::interval) AT TIME ZONE 'utc'::text))) THEN sales_summary.wax_price
            ELSE (0)::double precision
        END) AS wax_volume_day_6,
    sum(
        CASE
            WHEN ((sales_summary."timestamp" >= ((now() - '3 days'::interval) AT TIME ZONE 'utc'::text)) AND (sales_summary."timestamp" <= ((now() - '2 days'::interval) AT TIME ZONE 'utc'::text))) THEN sales_summary.wax_price
            ELSE (0)::double precision
        END) AS wax_volume_day_5,
    sum(
        CASE
            WHEN ((sales_summary."timestamp" >= ((now() - '4 days'::interval) AT TIME ZONE 'utc'::text)) AND (sales_summary."timestamp" <= ((now() - '3 days'::interval) AT TIME ZONE 'utc'::text))) THEN sales_summary.wax_price
            ELSE (0)::double precision
        END) AS wax_volume_day_4,
    sum(
        CASE
            WHEN ((sales_summary."timestamp" >= ((now() - '5 days'::interval) AT TIME ZONE 'utc'::text)) AND (sales_summary."timestamp" <= ((now() - '4 days'::interval) AT TIME ZONE 'utc'::text))) THEN sales_summary.wax_price
            ELSE (0)::double precision
        END) AS wax_volume_day_3,
    sum(
        CASE
            WHEN ((sales_summary."timestamp" >= ((now() - '6 days'::interval) AT TIME ZONE 'utc'::text)) AND (sales_summary."timestamp" <= ((now() - '5 days'::interval) AT TIME ZONE 'utc'::text))) THEN sales_summary.wax_price
            ELSE (0)::double precision
        END) AS wax_volume_day_2,
    sum(
        CASE
            WHEN ((sales_summary."timestamp" >= ((now() - '7 days'::interval) AT TIME ZONE 'utc'::text)) AND (sales_summary."timestamp" <= ((now() - '6 days'::interval) AT TIME ZONE 'utc'::text))) THEN sales_summary.wax_price
            ELSE (0)::double precision
        END) AS wax_volume_day_1,
    sales_summary.collection,
    sales_summary.type
   FROM public.sales_summary
  WHERE (sales_summary."timestamp" > ((now() - '7 days'::interval) AT TIME ZONE 'utc'::text))
  GROUP BY sales_summary.collection, sales_summary.type
  WITH NO DATA;


ALTER TABLE public.sales_seven_day_chart_mv OWNER TO postgres;

--
-- Name: schema_stats_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.schema_stats_mv AS
 SELECT t.collection,
    t.schema,
    sum(ts.volume_wax) AS volume_wax,
    sum(ts.volume_usd) AS volume_usd,
    (sum(ts.num_sales))::integer AS num_sales,
    (sum(tm.num_minted))::integer AS num_minted,
    (sum(tm.num_burned))::integer AS num_burned,
    (count(DISTINCT t.template_id))::integer AS num_templates
   FROM ((public.templates t
     LEFT JOIN public.template_stats_mv ts USING (template_id))
     LEFT JOIN public.templates_minted_mv tm USING (template_id))
  GROUP BY t.collection, t.schema
  WITH NO DATA;


ALTER TABLE public.schema_stats_mv OWNER TO postgres;

--
-- Name: schemas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.schemas (
    schema character varying(16),
    collection character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    schema_format json
);


ALTER TABLE public.schemas OWNER TO postgres;

--
-- Name: secondary_market_purchases; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.secondary_market_purchases (
    asset_ids bigint[],
    collection character varying(13),
    seller character varying(13),
    buyer character varying(13),
    market character varying(13),
    maker character varying(13),
    taker character varying(13),
    price double precision,
    currency character varying(12),
    usd_price double precision,
    listing_id bigint,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.secondary_market_purchases OWNER TO postgres;

--
-- Name: seller_volumes_1_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.seller_volumes_1_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales,
    t.seller,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '1 day'::interval))
  GROUP BY t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.seller_volumes_1_mv OWNER TO postgres;

--
-- Name: seller_volumes_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.seller_volumes_mv AS
 SELECT sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '1 day'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
            ELSE (0)::double precision
        END) AS wax_volume_1_day,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '1 day'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.usd_price
            ELSE (0)::double precision
        END) AS usd_volume_1_day,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '2 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
            ELSE (0)::double precision
        END) AS wax_volume_2_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '2 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.usd_price
            ELSE (0)::double precision
        END) AS usd_volume_2_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '3 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
            ELSE (0)::double precision
        END) AS wax_volume_3_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '3 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.usd_price
            ELSE (0)::double precision
        END) AS usd_volume_3_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '7 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
            ELSE (0)::double precision
        END) AS wax_volume_7_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '7 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.usd_price
            ELSE (0)::double precision
        END) AS usd_volume_7_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '14 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
            ELSE (0)::double precision
        END) AS wax_volume_14_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '14 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.usd_price
            ELSE (0)::double precision
        END) AS usd_volume_14_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '30 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
            ELSE (0)::double precision
        END) AS wax_volume_30_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '30 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.usd_price
            ELSE (0)::double precision
        END) AS usd_volume_30_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '60 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
            ELSE (0)::double precision
        END) AS wax_volume_60_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '60 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.usd_price
            ELSE (0)::double precision
        END) AS usd_volume_60_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '90 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
            ELSE (0)::double precision
        END) AS wax_volume_90_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '90 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.usd_price
            ELSE (0)::double precision
        END) AS usd_volume_90_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '180 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
            ELSE (0)::double precision
        END) AS wax_volume_180_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '180 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.usd_price
            ELSE (0)::double precision
        END) AS usd_volume_180_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '365 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
            ELSE (0)::double precision
        END) AS wax_volume_365_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '365 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.usd_price
            ELSE (0)::double precision
        END) AS usd_volume_365_days,
    sum(sales_summary.wax_price) AS wax_volume_all_time,
    sum(sales_summary.usd_price) AS usd_volume_all_time,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '1 day'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.num_items
            ELSE 0
        END) AS purchases_1_day,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '2 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.num_items
            ELSE 0
        END) AS purchases_2_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '3 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.num_items
            ELSE 0
        END) AS purchases_3_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '7 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.num_items
            ELSE 0
        END) AS purchases_7_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '14 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.num_items
            ELSE 0
        END) AS purchases_14_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '30 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.num_items
            ELSE 0
        END) AS purchases_30_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '60 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.num_items
            ELSE 0
        END) AS purchases_60_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '90 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.num_items
            ELSE 0
        END) AS purchases_90_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '180 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.num_items
            ELSE 0
        END) AS purchases_180_days,
    sum(
        CASE
            WHEN (sales_summary."timestamp" > ((now() - '365 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.num_items
            ELSE 0
        END) AS purchases_365_days,
    sum(sales_summary.num_items) AS purchases_all_time,
    sales_summary.seller AS user_name,
    sales_summary.type,
    sales_summary.collection
   FROM public.sales_summary
  GROUP BY sales_summary.seller, sales_summary.type, sales_summary.collection
  WITH NO DATA;


ALTER TABLE public.seller_volumes_mv OWNER TO postgres;

--
-- Name: tables_with_seq; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.tables_with_seq AS
 SELECT t.table_schema,
    t.table_name
   FROM (information_schema.tables t
     JOIN information_schema.columns c ON ((((c.table_name)::name = (t.table_name)::name) AND ((c.table_schema)::name = (t.table_schema)::name))))
  WHERE (((c.column_name)::name = 'seq'::name) AND ((t.table_schema)::name <> ALL (ARRAY['information_schema'::name, 'pg_catalog'::name])) AND ((t.table_type)::text = 'BASE TABLE'::text))
  ORDER BY t.table_schema;


ALTER TABLE public.tables_with_seq OWNER TO postgres;

--
-- Name: seq_index_creation; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.seq_index_creation AS
 SELECT ((' CREATE INDEX ON '::text || (f.table_name)::text) || ' (seq DESC) ;'::text) AS "?column?"
   FROM ( SELECT tables_with_seq.table_name
           FROM public.tables_with_seq
          WHERE (NOT ((tables_with_seq.table_name)::name IN ( SELECT indexes.table_name
                   FROM public.indexes
                  WHERE (indexes.column_name = 'seq'::name))))) f;


ALTER TABLE public.seq_index_creation OWNER TO postgres;

--
-- Name: sets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sets (
    collection character varying(13),
    schema character varying(13),
    attribute_ids integer[],
    total integer,
    name_id integer,
    set_id integer NOT NULL
);


ALTER TABLE public.sets OWNER TO postgres;

--
-- Name: sets_set_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sets_set_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sets_set_id_seq OWNER TO postgres;

--
-- Name: sets_set_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sets_set_id_seq OWNED BY public.sets.set_id;


--
-- Name: simpleassets_burns; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.simpleassets_burns (
    asset_ids bigint[],
    burner character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.simpleassets_burns OWNER TO postgres;

--
-- Name: simpleassets_burns_reversed; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.simpleassets_burns_reversed (
    asset_ids bigint[],
    burner character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.simpleassets_burns_reversed OWNER TO postgres;

--
-- Name: simpleassets_burns_unnested; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.simpleassets_burns_unnested (
    asset_id bigint
);


ALTER TABLE public.simpleassets_burns_unnested OWNER TO postgres;

--
-- Name: simpleassets_claims; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.simpleassets_claims (
    asset_id bigint,
    claimer character varying(12),
    old_owner character varying(12),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.simpleassets_claims OWNER TO postgres;

--
-- Name: simpleassets_offers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.simpleassets_offers (
    asset_ids bigint[],
    owner character varying(12),
    newowner character varying(12),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    memo_id integer
);


ALTER TABLE public.simpleassets_offers OWNER TO postgres;

--
-- Name: simpleassets_updates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.simpleassets_updates (
    asset_id bigint,
    new_mdata_id integer,
    old_mdata_id integer,
    applied boolean DEFAULT false,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.simpleassets_updates OWNER TO postgres;

--
-- Name: simpleassets_updates_max_seqs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.simpleassets_updates_max_seqs (
    asset_id bigint,
    seq bigint
);


ALTER TABLE public.simpleassets_updates_max_seqs OWNER TO postgres;

--
-- Name: simpleassets_updates_reversed; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.simpleassets_updates_reversed (
    asset_id bigint,
    new_mdata_id integer,
    old_mdata_id integer,
    applied boolean,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.simpleassets_updates_reversed OWNER TO postgres;

--
-- Name: simplemarket_buylogs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.simplemarket_buylogs (
    transaction_id character varying(128),
    seq bigint,
    "timestamp" timestamp without time zone,
    price double precision,
    currency character varying(3),
    buyer character varying(12),
    sellid bigint
);


ALTER TABLE public.simplemarket_buylogs OWNER TO postgres;

--
-- Name: simplemarket_cancels; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.simplemarket_cancels (
    asset_ids bigint[],
    owner character varying(12),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.simplemarket_cancels OWNER TO postgres;

--
-- Name: simplemarket_purchases; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.simplemarket_purchases (
    asset_id bigint,
    seller character varying(13),
    buyer character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    price double precision,
    currency character varying(12)
);


ALTER TABLE public.simplemarket_purchases OWNER TO postgres;

--
-- Name: simplemarket_updates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.simplemarket_updates (
    sale_id bigint,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    new_price double precision,
    currency character varying(12),
    offer_price double precision,
    offer_currency character varying(6),
    offer_time timestamp without time zone,
    old_price double precision,
    old_currency character varying(12)
);


ALTER TABLE public.simplemarket_updates OWNER TO postgres;

--
-- Name: sold_atomicmarket_template_buy_offers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sold_atomicmarket_template_buy_offers (
    buyoffer_id bigint,
    buyer character varying(13),
    price double precision,
    currency character varying(12),
    template_id bigint,
    maker character varying(13),
    taker character varying(13),
    collection character varying(13),
    collection_fee double precision,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.sold_atomicmarket_template_buy_offers OWNER TO postgres;

--
-- Name: stake_accounts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.stake_accounts (
    account character varying(13)
);


ALTER TABLE public.stake_accounts OWNER TO postgres;

--
-- Name: stakes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.stakes (
    asset_id bigint,
    stake_contract character varying(13),
    staker character varying(13),
    memo character varying(256),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.stakes OWNER TO postgres;

--
-- Name: table_sizes; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.table_sizes AS
 WITH RECURSIVE pg_inherit(inhrelid, inhparent) AS (
         SELECT pg_inherits.inhrelid,
            pg_inherits.inhparent
           FROM pg_inherits
        UNION
         SELECT child.inhrelid,
            parent.inhparent
           FROM pg_inherit child,
            pg_inherits parent
          WHERE (child.inhparent = parent.inhrelid)
        ), pg_inherit_short AS (
         SELECT pg_inherit.inhrelid,
            pg_inherit.inhparent
           FROM pg_inherit
          WHERE (NOT (pg_inherit.inhparent IN ( SELECT pg_inherit_1.inhrelid
                   FROM pg_inherit pg_inherit_1)))
        )
 SELECT a.table_schema,
    a.table_name,
    a.row_estimate,
    pg_size_pretty(a.total_bytes) AS total,
    pg_size_pretty(a.index_bytes) AS index,
    pg_size_pretty(a.toast_bytes) AS toast,
    pg_size_pretty(a.table_bytes) AS "table",
    ((a.total_bytes)::double precision / (sum(a.total_bytes) OVER ())::double precision) AS total_size_share
   FROM ( SELECT a_1.oid,
            a_1.table_schema,
            a_1.table_name,
            a_1.row_estimate,
            a_1.total_bytes,
            a_1.index_bytes,
            a_1.toast_bytes,
            a_1.parent,
            ((a_1.total_bytes - a_1.index_bytes) - COALESCE(a_1.toast_bytes, (0)::numeric)) AS table_bytes
           FROM ( SELECT c.oid,
                    n.nspname AS table_schema,
                    c.relname AS table_name,
                    sum(c.reltuples) OVER (PARTITION BY c.parent) AS row_estimate,
                    sum(pg_total_relation_size((c.oid)::regclass)) OVER (PARTITION BY c.parent) AS total_bytes,
                    sum(pg_indexes_size((c.oid)::regclass)) OVER (PARTITION BY c.parent) AS index_bytes,
                    sum(pg_total_relation_size((c.reltoastrelid)::regclass)) OVER (PARTITION BY c.parent) AS toast_bytes,
                    c.parent
                   FROM (( SELECT pg_class.oid,
                            pg_class.reltuples,
                            pg_class.relname,
                            pg_class.relnamespace,
                            pg_class.reltoastrelid,
                            COALESCE(pg_inherit_short.inhparent, pg_class.oid) AS parent
                           FROM (pg_class
                             LEFT JOIN pg_inherit_short ON ((pg_inherit_short.inhrelid = pg_class.oid)))
                          WHERE (pg_class.relkind = ANY (ARRAY['r'::"char", 'p'::"char"]))) c
                     LEFT JOIN pg_namespace n ON ((n.oid = c.relnamespace)))) a_1
          WHERE (a_1.oid = a_1.parent)) a
  ORDER BY a.total_bytes DESC;


ALTER TABLE public.table_sizes OWNER TO postgres;

--
-- Name: tag_filter_actions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tag_filter_actions (
    user_name character varying(13),
    tag_id integer,
    action_name character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.tag_filter_actions OWNER TO postgres;

--
-- Name: tag_filters_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.tag_filters_mv AS
 SELECT t.user_name,
    t.tag_id
   FROM public.tag_filter_actions t
  WHERE (((t.action_name)::text = 'addfilter'::text) AND (t.seq = ( SELECT max(tag_filter_actions.seq) AS max
           FROM public.tag_filter_actions
          WHERE (((tag_filter_actions.user_name)::text = (t.user_name)::text) AND (tag_filter_actions.tag_id = t.tag_id)))))
  WITH NO DATA;


ALTER TABLE public.tag_filters_mv OWNER TO postgres;

--
-- Name: tag_suggestions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tag_suggestions (
    suggester character varying(13),
    tag_id integer,
    collection character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.tag_suggestions OWNER TO postgres;

--
-- Name: tags_tag_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tags_tag_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tags_tag_id_seq OWNER TO postgres;

--
-- Name: tags_tag_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tags_tag_id_seq OWNED BY public.tags.tag_id;


--
-- Name: template_collection_sales_by_date_before_2024_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.template_collection_sales_by_date_before_2024_mv AS
 SELECT t.collection,
    t.schema,
    t.template_id,
    to_date(to_char(t."timestamp", 'YYYY/MM/DD'::text), 'YYYY/MM/DD'::text) AS to_date,
    sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(DISTINCT sales_summary.buyer) AS buyers,
    count(DISTINCT sales_summary.seller) AS sellers,
    count(1) AS sales
   FROM (public.template_sales t
     LEFT JOIN public.sales_summary USING (seq))
  WHERE (t."timestamp" < '2024-01-01 00:00:00'::timestamp without time zone)
  GROUP BY t.collection, t.schema, t.template_id, (to_date(to_char(t."timestamp", 'YYYY/MM/DD'::text), 'YYYY/MM/DD'::text))
  WITH NO DATA;


ALTER TABLE public.template_collection_sales_by_date_before_2024_mv OWNER TO postgres;

--
-- Name: template_collection_sales_by_date_from_2024_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.template_collection_sales_by_date_from_2024_mv AS
 SELECT t.collection,
    t.schema,
    t.template_id,
    to_date(to_char(t."timestamp", 'YYYY/MM/DD'::text), 'YYYY/MM/DD'::text) AS to_date,
    sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(DISTINCT sales_summary.buyer) AS buyers,
    count(DISTINCT sales_summary.seller) AS sellers,
    count(1) AS sales
   FROM (public.template_sales t
     LEFT JOIN public.sales_summary USING (seq))
  WHERE (t."timestamp" >= '2024-01-01 00:00:00'::timestamp without time zone)
  GROUP BY t.collection, t.schema, t.template_id, (to_date(to_char(t."timestamp", 'YYYY/MM/DD'::text), 'YYYY/MM/DD'::text))
  WITH NO DATA;


ALTER TABLE public.template_collection_sales_by_date_from_2024_mv OWNER TO postgres;

--
-- Name: template_collection_sales_by_date_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.template_collection_sales_by_date_mv AS
 SELECT template_collection_sales_by_date_from_2024_mv.collection,
    template_collection_sales_by_date_from_2024_mv.schema,
    template_collection_sales_by_date_from_2024_mv.template_id,
    template_collection_sales_by_date_from_2024_mv.to_date,
    template_collection_sales_by_date_from_2024_mv.wax_volume,
    template_collection_sales_by_date_from_2024_mv.usd_volume,
    template_collection_sales_by_date_from_2024_mv.buyers,
    template_collection_sales_by_date_from_2024_mv.sellers,
    template_collection_sales_by_date_from_2024_mv.sales
   FROM public.template_collection_sales_by_date_from_2024_mv
UNION ALL
 SELECT template_collection_sales_by_date_before_2024_mv.collection,
    template_collection_sales_by_date_before_2024_mv.schema,
    template_collection_sales_by_date_before_2024_mv.template_id,
    template_collection_sales_by_date_before_2024_mv.to_date,
    template_collection_sales_by_date_before_2024_mv.wax_volume,
    template_collection_sales_by_date_before_2024_mv.usd_volume,
    template_collection_sales_by_date_before_2024_mv.buyers,
    template_collection_sales_by_date_before_2024_mv.sellers,
    template_collection_sales_by_date_before_2024_mv.sales
   FROM public.template_collection_sales_by_date_before_2024_mv
  WITH NO DATA;


ALTER TABLE public.template_collection_sales_by_date_mv OWNER TO postgres;

--
-- Name: token_updates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.token_updates (
    contract character varying(13),
    symbol character varying(12),
    decimals integer,
    old_decimals integer,
    maximum_supply double precision,
    old_maximum_supply double precision,
    token_name character varying(64),
    old_token_name character varying(64),
    token_logo character varying(256),
    old_token_logo character varying(256),
    token_logo_lg character varying(256),
    old_token_logo_lg character varying(256),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.token_updates OWNER TO postgres;

--
-- Name: tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tokens (
    contract character varying(13),
    symbol character varying(12),
    decimals integer,
    maximum_supply double precision,
    token_name character varying(64),
    token_logo character varying(256),
    token_logo_lg character varying(256),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.tokens OWNER TO postgres;

--
-- Name: transaction_ids; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.transaction_ids (
    transaction_id integer NOT NULL,
    hash character varying(64)
);


ALTER TABLE public.transaction_ids OWNER TO postgres;

--
-- Name: transaction_ids_transaction_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.transaction_ids_transaction_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.transaction_ids_transaction_id_seq OWNER TO postgres;

--
-- Name: transaction_ids_transaction_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.transaction_ids_transaction_id_seq OWNED BY public.transaction_ids.transaction_id;


--
-- Name: transactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.transactions (
    id integer NOT NULL,
    transaction_id character varying(64),
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.transactions OWNER TO postgres;

--
-- Name: transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.transactions_id_seq OWNER TO postgres;

--
-- Name: transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.transactions_id_seq OWNED BY public.transactions.id;


--
-- Name: transfers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.transfers (
    asset_ids bigint[],
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    sender character varying(12),
    receiver character varying(12),
    memo_id integer,
    applied boolean DEFAULT false
);


ALTER TABLE public.transfers OWNER TO postgres;

--
-- Name: transfers_reversed; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.transfers_reversed (
    asset_ids bigint[],
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    sender character varying(13),
    receiver character varying(13),
    memo_id integer,
    applied boolean
);


ALTER TABLE public.transfers_reversed OWNER TO postgres;

--
-- Name: twitch_benefits; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.twitch_benefits (
    id character varying(128),
    benefit_id character varying(40),
    "timestamp" timestamp without time zone,
    user_id bigint,
    game_id bigint,
    fulfillment_status character varying(12),
    last_updated timestamp without time zone,
    pushed boolean
);


ALTER TABLE public.twitch_benefits OWNER TO postgres;

--
-- Name: twitch_claims; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.twitch_claims (
    drop_id bigint,
    contract character varying(13),
    claimer character varying(13),
    benefit_id character varying(40),
    reward_id bigint,
    reward_string character varying(128),
    updated boolean,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.twitch_claims OWNER TO postgres;

--
-- Name: twitch_clients; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.twitch_clients (
    client_id character varying(32),
    client_secret character varying(32),
    access_token character varying(32)
);


ALTER TABLE public.twitch_clients OWNER TO postgres;

--
-- Name: twitch_drops; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.twitch_drops (
    drop_id bigint,
    contract character varying(13),
    benefit_id character varying(40),
    game_id bigint,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.twitch_drops OWNER TO postgres;

--
-- Name: twitch_games; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.twitch_games (
    game_id bigint,
    client_id character varying(32),
    client_secret character varying(32),
    access_token character varying(32),
    fetch_rewards boolean,
    cursor text
);


ALTER TABLE public.twitch_games OWNER TO postgres;

--
-- Name: twitch_users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.twitch_users (
    user_id bigint,
    wallet character varying(13),
    login character varying(128),
    display_name character varying(128),
    email character varying(128)
);


ALTER TABLE public.twitch_users OWNER TO postgres;

--
-- Name: universal_previews; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.universal_previews (
    image_id integer,
    video_id integer,
    size integer
);


ALTER TABLE public.universal_previews OWNER TO postgres;

--
-- Name: unverify_overwrite; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.unverify_overwrite (
    collection character varying(13)
);


ALTER TABLE public.unverify_overwrite OWNER TO postgres;

--
-- Name: user_collection_volumes_from_2023_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.user_collection_volumes_from_2023_mv AS
 SELECT sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales,
    t.collection,
    t.seller,
    t.buyer,
    t.type
   FROM public.sales_summary t
  WHERE (t."timestamp" > '2023-01-01 00:00:00'::timestamp without time zone)
  GROUP BY t.collection, t.seller, t.buyer, t.type
  WITH NO DATA;


ALTER TABLE public.user_collection_volumes_from_2023_mv OWNER TO postgres;

--
-- Name: user_collection_volumes_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.user_collection_volumes_mv AS
 SELECT sum(t.wax_volume_1_day) AS wax_volume_1_day,
    sum(t.usd_volume_1_day) AS usd_volume_1_day,
    sum(t.wax_volume_2_days) AS wax_volume_2_days,
    sum(t.usd_volume_2_days) AS usd_volume_2_days,
    sum(t.wax_volume_3_days) AS wax_volume_3_days,
    sum(t.usd_volume_3_days) AS usd_volume_3_days,
    sum(t.wax_volume_7_days) AS wax_volume_7_days,
    sum(t.usd_volume_7_days) AS usd_volume_7_days,
    sum(t.wax_volume_14_days) AS wax_volume_14_days,
    sum(t.usd_volume_14_days) AS usd_volume_14_days,
    sum(t.wax_volume_30_days) AS wax_volume_30_days,
    sum(t.usd_volume_30_days) AS usd_volume_30_days,
    sum(t.wax_volume_60_days) AS wax_volume_60_days,
    sum(t.usd_volume_60_days) AS usd_volume_60_days,
    sum(t.wax_volume_90_days) AS wax_volume_90_days,
    sum(t.usd_volume_90_days) AS usd_volume_90_days,
    sum(t.wax_volume_180_days) AS wax_volume_180_days,
    sum(t.usd_volume_180_days) AS usd_volume_180_days,
    sum(t.wax_volume_365_days) AS wax_volume_365_days,
    sum(t.usd_volume_365_days) AS usd_volume_365_days,
    sum(t.wax_volume_all_time) AS wax_volume_all_time,
    sum(t.usd_volume_all_time) AS usd_volume_all_time,
    sum(t.purchases_1_day) AS purchases_1_day,
    sum(t.purchases_2_days) AS purchases_2_days,
    sum(t.purchases_3_days) AS purchases_3_days,
    sum(t.purchases_7_days) AS purchases_7_days,
    sum(t.purchases_14_days) AS purchases_14_days,
    sum(t.purchases_30_days) AS purchases_30_days,
    sum(t.purchases_60_days) AS purchases_60_days,
    sum(t.purchases_90_days) AS purchases_90_days,
    sum(t.purchases_180_days) AS purchases_180_days,
    sum(t.purchases_365_days) AS purchases_365_days,
    sum(t.purchases_all_time) AS purchases_all_time,
    t.user_name,
    t.type,
    t.actor,
    t.collection
   FROM ( SELECT buyer_volumes_mv.wax_volume_1_day,
            buyer_volumes_mv.usd_volume_1_day,
            buyer_volumes_mv.wax_volume_2_days,
            buyer_volumes_mv.usd_volume_2_days,
            buyer_volumes_mv.wax_volume_3_days,
            buyer_volumes_mv.usd_volume_3_days,
            buyer_volumes_mv.wax_volume_7_days,
            buyer_volumes_mv.usd_volume_7_days,
            buyer_volumes_mv.wax_volume_14_days,
            buyer_volumes_mv.usd_volume_14_days,
            buyer_volumes_mv.wax_volume_30_days,
            buyer_volumes_mv.usd_volume_30_days,
            buyer_volumes_mv.wax_volume_60_days,
            buyer_volumes_mv.usd_volume_60_days,
            buyer_volumes_mv.wax_volume_90_days,
            buyer_volumes_mv.usd_volume_90_days,
            buyer_volumes_mv.wax_volume_180_days,
            buyer_volumes_mv.usd_volume_180_days,
            buyer_volumes_mv.wax_volume_365_days,
            buyer_volumes_mv.usd_volume_365_days,
            buyer_volumes_mv.wax_volume_all_time,
            buyer_volumes_mv.usd_volume_all_time,
            buyer_volumes_mv.purchases_1_day,
            buyer_volumes_mv.purchases_2_days,
            buyer_volumes_mv.purchases_3_days,
            buyer_volumes_mv.purchases_7_days,
            buyer_volumes_mv.purchases_14_days,
            buyer_volumes_mv.purchases_30_days,
            buyer_volumes_mv.purchases_60_days,
            buyer_volumes_mv.purchases_90_days,
            buyer_volumes_mv.purchases_180_days,
            buyer_volumes_mv.purchases_365_days,
            buyer_volumes_mv.purchases_all_time,
            buyer_volumes_mv.user_name,
            buyer_volumes_mv.type,
            buyer_volumes_mv.collection,
            'buyer'::text AS actor
           FROM public.buyer_volumes_mv
        UNION
         SELECT seller_volumes_mv.wax_volume_1_day,
            seller_volumes_mv.usd_volume_1_day,
            seller_volumes_mv.wax_volume_2_days,
            seller_volumes_mv.usd_volume_2_days,
            seller_volumes_mv.wax_volume_3_days,
            seller_volumes_mv.usd_volume_3_days,
            seller_volumes_mv.wax_volume_7_days,
            seller_volumes_mv.usd_volume_7_days,
            seller_volumes_mv.wax_volume_14_days,
            seller_volumes_mv.usd_volume_14_days,
            seller_volumes_mv.wax_volume_30_days,
            seller_volumes_mv.usd_volume_30_days,
            seller_volumes_mv.wax_volume_60_days,
            seller_volumes_mv.usd_volume_60_days,
            seller_volumes_mv.wax_volume_90_days,
            seller_volumes_mv.usd_volume_90_days,
            seller_volumes_mv.wax_volume_180_days,
            seller_volumes_mv.usd_volume_180_days,
            seller_volumes_mv.wax_volume_365_days,
            seller_volumes_mv.usd_volume_365_days,
            seller_volumes_mv.wax_volume_all_time,
            seller_volumes_mv.usd_volume_all_time,
            seller_volumes_mv.purchases_1_day,
            seller_volumes_mv.purchases_2_days,
            seller_volumes_mv.purchases_3_days,
            seller_volumes_mv.purchases_7_days,
            seller_volumes_mv.purchases_14_days,
            seller_volumes_mv.purchases_30_days,
            seller_volumes_mv.purchases_60_days,
            seller_volumes_mv.purchases_90_days,
            seller_volumes_mv.purchases_180_days,
            seller_volumes_mv.purchases_365_days,
            seller_volumes_mv.purchases_all_time,
            seller_volumes_mv.user_name,
            seller_volumes_mv.type,
            seller_volumes_mv.collection,
            'seller'::text AS actor
           FROM public.seller_volumes_mv) t
  GROUP BY t.user_name, t.type, t.actor, t.collection
  ORDER BY (sum(t.wax_volume_1_day)) DESC
  WITH NO DATA;


ALTER TABLE public.user_collection_volumes_mv OWNER TO postgres;

--
-- Name: user_collection_volumes_s_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.user_collection_volumes_s_mv AS
 SELECT sum(t.wax_volume_1_day) AS wax_volume_1_day,
    sum(t.usd_volume_1_day) AS usd_volume_1_day,
    sum(t.wax_volume_2_days) AS wax_volume_2_days,
    sum(t.usd_volume_2_days) AS usd_volume_2_days,
    sum(t.wax_volume_3_days) AS wax_volume_3_days,
    sum(t.usd_volume_3_days) AS usd_volume_3_days,
    sum(t.wax_volume_7_days) AS wax_volume_7_days,
    sum(t.usd_volume_7_days) AS usd_volume_7_days,
    count(t.purchases_1_day) AS purchases_1_day,
    sum(t.purchases_2_days) AS purchases_2_days,
    sum(t.purchases_3_days) AS purchases_3_days,
    sum(t.purchases_7_days) AS purchases_7_days,
    t.user_name,
    t.type,
    t.collection,
    t.actor
   FROM ( SELECT
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '1 day'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
                    ELSE (0)::double precision
                END AS wax_volume_1_day,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '1 day'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.usd_price
                    ELSE (0)::double precision
                END AS usd_volume_1_day,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '2 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
                    ELSE (0)::double precision
                END AS wax_volume_2_days,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '2 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.usd_price
                    ELSE (0)::double precision
                END AS usd_volume_2_days,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '3 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
                    ELSE (0)::double precision
                END AS wax_volume_3_days,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '3 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.usd_price
                    ELSE (0)::double precision
                END AS usd_volume_3_days,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '7 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
                    ELSE (0)::double precision
                END AS wax_volume_7_days,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '7 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.usd_price
                    ELSE (0)::double precision
                END AS usd_volume_7_days,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '1 day'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.num_items
                    ELSE 0
                END AS purchases_1_day,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '2 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.num_items
                    ELSE 0
                END AS purchases_2_days,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '3 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.num_items
                    ELSE 0
                END AS purchases_3_days,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '7 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.num_items
                    ELSE 0
                END AS purchases_7_days,
            sales_summary.buyer AS user_name,
            sales_summary.type,
            sales_summary.collection,
            'buyer'::text AS actor
           FROM public.sales_summary
          WHERE (sales_summary."timestamp" > ((now() - '7 days'::interval) AT TIME ZONE 'utc'::text))
        UNION
         SELECT
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '1 day'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
                    ELSE (0)::double precision
                END AS wax_volume_1_day,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '1 day'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.usd_price
                    ELSE (0)::double precision
                END AS usd_volume_1_day,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '2 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
                    ELSE (0)::double precision
                END AS wax_volume_2_days,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '2 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.usd_price
                    ELSE (0)::double precision
                END AS usd_volume_2_days,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '3 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
                    ELSE (0)::double precision
                END AS wax_volume_3_days,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '3 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.usd_price
                    ELSE (0)::double precision
                END AS usd_volume_3_days,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '7 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.wax_price
                    ELSE (0)::double precision
                END AS wax_volume_7_days,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '7 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.usd_price
                    ELSE (0)::double precision
                END AS usd_volume_7_days,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '1 day'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.num_items
                    ELSE 0
                END AS purchases_1_day,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '2 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.num_items
                    ELSE 0
                END AS purchases_2_days,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '3 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.num_items
                    ELSE 0
                END AS purchases_3_days,
                CASE
                    WHEN (sales_summary."timestamp" > ((now() - '7 days'::interval) AT TIME ZONE 'utc'::text)) THEN sales_summary.num_items
                    ELSE 0
                END AS purchases_7_days,
            sales_summary.seller AS user_name,
            sales_summary.type,
            sales_summary.collection,
            'seller'::text AS actor
           FROM public.sales_summary
          WHERE (sales_summary."timestamp" > ((now() - '7 days'::interval) AT TIME ZONE 'utc'::text))) t
  GROUP BY t.user_name, t.type, t.collection, t.actor
  ORDER BY (sum(t.wax_volume_1_day)) DESC
  WITH NO DATA;


ALTER TABLE public.user_collection_volumes_s_mv OWNER TO postgres;

--
-- Name: user_picture_updates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_picture_updates (
    user_name character varying(13),
    image_id integer,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.user_picture_updates OWNER TO postgres;

--
-- Name: user_pictures_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.user_pictures_mv AS
 SELECT u.user_name,
    i.image
   FROM (public.user_picture_updates u
     LEFT JOIN public.images i USING (image_id))
  WHERE (u.seq = ( SELECT max(user_picture_updates.seq) AS max
           FROM public.user_picture_updates
          WHERE ((user_picture_updates.user_name)::text = (u.user_name)::text)))
  WITH NO DATA;


ALTER TABLE public.user_pictures_mv OWNER TO postgres;

--
-- Name: user_volumes_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.user_volumes_mv AS
 SELECT sum(t.wax_volume_1_day) AS wax_volume_1_day,
    sum(t.usd_volume_1_day) AS usd_volume_1_day,
    sum(t.wax_volume_2_days) AS wax_volume_2_days,
    sum(t.usd_volume_2_days) AS usd_volume_2_days,
    sum(t.wax_volume_3_days) AS wax_volume_3_days,
    sum(t.usd_volume_3_days) AS usd_volume_3_days,
    sum(t.wax_volume_7_days) AS wax_volume_7_days,
    sum(t.usd_volume_7_days) AS usd_volume_7_days,
    sum(t.wax_volume_14_days) AS wax_volume_14_days,
    sum(t.usd_volume_14_days) AS usd_volume_14_days,
    sum(t.wax_volume_30_days) AS wax_volume_30_days,
    sum(t.usd_volume_30_days) AS usd_volume_30_days,
    sum(t.wax_volume_60_days) AS wax_volume_60_days,
    sum(t.usd_volume_60_days) AS usd_volume_60_days,
    sum(t.wax_volume_90_days) AS wax_volume_90_days,
    sum(t.usd_volume_90_days) AS usd_volume_90_days,
    sum(t.wax_volume_180_days) AS wax_volume_180_days,
    sum(t.usd_volume_180_days) AS usd_volume_180_days,
    sum(t.wax_volume_365_days) AS wax_volume_365_days,
    sum(t.usd_volume_365_days) AS usd_volume_365_days,
    sum(t.wax_volume_all_time) AS wax_volume_all_time,
    sum(t.usd_volume_all_time) AS usd_volume_all_time,
    sum(t.purchases_1_day) AS purchases_1_day,
    sum(t.purchases_2_days) AS purchases_2_days,
    sum(t.purchases_3_days) AS purchases_3_days,
    sum(t.purchases_7_days) AS purchases_7_days,
    sum(t.purchases_14_days) AS purchases_14_days,
    sum(t.purchases_30_days) AS purchases_30_days,
    sum(t.purchases_60_days) AS purchases_60_days,
    sum(t.purchases_90_days) AS purchases_90_days,
    sum(t.purchases_180_days) AS purchases_180_days,
    sum(t.purchases_365_days) AS purchases_365_days,
    sum(t.purchases_all_time) AS purchases_all_time,
    t.user_name,
    t.type,
    t.actor
   FROM public.user_collection_volumes_mv t
  GROUP BY t.user_name, t.type, t.actor
  WITH NO DATA;


ALTER TABLE public.user_volumes_mv OWNER TO postgres;

--
-- Name: user_volumes_s_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.user_volumes_s_mv AS
 SELECT sum(t.wax_volume_1_day) AS wax_volume_1_day,
    sum(t.usd_volume_1_day) AS usd_volume_1_day,
    sum(t.wax_volume_2_days) AS wax_volume_2_days,
    sum(t.usd_volume_2_days) AS usd_volume_2_days,
    sum(t.wax_volume_3_days) AS wax_volume_3_days,
    sum(t.usd_volume_3_days) AS usd_volume_3_days,
    sum(t.wax_volume_7_days) AS wax_volume_7_days,
    sum(t.usd_volume_7_days) AS usd_volume_7_days,
    sum(t.purchases_1_day) AS purchases_1_day,
    sum(t.purchases_2_days) AS purchases_2_days,
    sum(t.purchases_3_days) AS purchases_3_days,
    sum(t.purchases_7_days) AS purchases_7_days,
    t.user_name,
    t.type,
    t.actor
   FROM public.user_collection_volumes_s_mv t
  GROUP BY t.user_name, t.type, t.actor
  WITH NO DATA;


ALTER TABLE public.user_volumes_s_mv OWNER TO postgres;

--
-- Name: users_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.users_mv AS
 SELECT collection_users_mv.owner,
    sum(collection_users_mv.num_assets) AS num_assets,
    sum(collection_users_mv.wax_value) AS wax_value,
    sum(collection_users_mv.usd_value) AS usd_value
   FROM public.collection_users_mv
  GROUP BY collection_users_mv.owner
  WITH NO DATA;


ALTER TABLE public.users_mv OWNER TO postgres;

--
-- Name: verification_actions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.verification_actions (
    collection character varying(13),
    action_name character varying(13),
    account character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone,
    added boolean DEFAULT false
);


ALTER TABLE public.verification_actions OWNER TO postgres;

--
-- Name: videos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.videos (
    video_id integer NOT NULL,
    video character varying(256)
);


ALTER TABLE public.videos OWNER TO postgres;

--
-- Name: videos_video_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.videos_video_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.videos_video_id_seq OWNER TO postgres;

--
-- Name: videos_video_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.videos_video_id_seq OWNED BY public.videos.video_id;


--
-- Name: volume_collection_market_user_14_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_market_user_14_days_mv AS
 SELECT t.collection,
    t.market,
    t.maker,
    t.taker,
    t.buyer,
    t.seller,
    t.type,
    sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'UTC'::text) - '14 days'::interval))
  GROUP BY t.collection, t.market, t.maker, t.taker, t.buyer, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_market_user_14_days_mv OWNER TO root;

--
-- Name: volume_buyer_14_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_buyer_14_days_mv AS
 SELECT t.buyer,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_14_days_mv t
  GROUP BY t.buyer, t.type
  WITH NO DATA;


ALTER TABLE public.volume_buyer_14_days_mv OWNER TO root;

--
-- Name: volume_collection_market_user_15_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_market_user_15_days_mv AS
 SELECT t.collection,
    t.market,
    t.maker,
    t.taker,
    t.buyer,
    t.seller,
    t.type,
    sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'UTC'::text) - '15 days'::interval))
  GROUP BY t.collection, t.market, t.maker, t.taker, t.buyer, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_market_user_15_days_mv OWNER TO root;

--
-- Name: volume_buyer_15_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_buyer_15_days_mv AS
 SELECT t.buyer,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_15_days_mv t
  GROUP BY t.buyer, t.type
  WITH NO DATA;


ALTER TABLE public.volume_buyer_15_days_mv OWNER TO root;

--
-- Name: volume_collection_market_user_180_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_market_user_180_days_mv AS
 SELECT t.collection,
    t.market,
    t.maker,
    t.taker,
    t.buyer,
    t.seller,
    t.type,
    sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'UTC'::text) - '180 days'::interval))
  GROUP BY t.collection, t.market, t.maker, t.taker, t.buyer, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_market_user_180_days_mv OWNER TO root;

--
-- Name: volume_buyer_180_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_buyer_180_days_mv AS
 SELECT t.buyer,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_180_days_mv t
  GROUP BY t.buyer, t.type
  WITH NO DATA;


ALTER TABLE public.volume_buyer_180_days_mv OWNER TO root;

--
-- Name: volume_collection_market_user_1_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_market_user_1_days_mv AS
 SELECT t.collection,
    t.market,
    t.maker,
    t.taker,
    t.buyer,
    t.seller,
    t.type,
    sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'UTC'::text) - '1 day'::interval))
  GROUP BY t.collection, t.market, t.maker, t.taker, t.buyer, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_market_user_1_days_mv OWNER TO root;

--
-- Name: volume_buyer_1_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_buyer_1_days_mv AS
 SELECT t.buyer,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_1_days_mv t
  GROUP BY t.buyer, t.type
  WITH NO DATA;


ALTER TABLE public.volume_buyer_1_days_mv OWNER TO root;

--
-- Name: volume_collection_market_user_2_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_market_user_2_days_mv AS
 SELECT t.collection,
    t.market,
    t.maker,
    t.taker,
    t.buyer,
    t.seller,
    t.type,
    sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'UTC'::text) - '2 days'::interval))
  GROUP BY t.collection, t.market, t.maker, t.taker, t.buyer, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_market_user_2_days_mv OWNER TO root;

--
-- Name: volume_buyer_2_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_buyer_2_days_mv AS
 SELECT t.buyer,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_2_days_mv t
  GROUP BY t.buyer, t.type
  WITH NO DATA;


ALTER TABLE public.volume_buyer_2_days_mv OWNER TO root;

--
-- Name: volume_collection_market_user_30_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_market_user_30_days_mv AS
 SELECT t.collection,
    t.market,
    t.maker,
    t.taker,
    t.buyer,
    t.seller,
    t.type,
    sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'UTC'::text) - '30 days'::interval))
  GROUP BY t.collection, t.market, t.maker, t.taker, t.buyer, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_market_user_30_days_mv OWNER TO root;

--
-- Name: volume_buyer_30_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_buyer_30_days_mv AS
 SELECT t.buyer,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_30_days_mv t
  GROUP BY t.buyer, t.type
  WITH NO DATA;


ALTER TABLE public.volume_buyer_30_days_mv OWNER TO root;

--
-- Name: volume_collection_market_user_365_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_market_user_365_days_mv AS
 SELECT t.collection,
    t.market,
    t.maker,
    t.taker,
    t.buyer,
    t.seller,
    t.type,
    sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'UTC'::text) - '365 days'::interval))
  GROUP BY t.collection, t.market, t.maker, t.taker, t.buyer, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_market_user_365_days_mv OWNER TO root;

--
-- Name: volume_buyer_365_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_buyer_365_days_mv AS
 SELECT t.buyer,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_365_days_mv t
  GROUP BY t.buyer, t.type
  WITH NO DATA;


ALTER TABLE public.volume_buyer_365_days_mv OWNER TO root;

--
-- Name: volume_collection_market_user_3_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_market_user_3_days_mv AS
 SELECT t.collection,
    t.market,
    t.maker,
    t.taker,
    t.buyer,
    t.seller,
    t.type,
    sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'UTC'::text) - '3 days'::interval))
  GROUP BY t.collection, t.market, t.maker, t.taker, t.buyer, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_market_user_3_days_mv OWNER TO root;

--
-- Name: volume_buyer_3_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_buyer_3_days_mv AS
 SELECT t.buyer,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_3_days_mv t
  GROUP BY t.buyer, t.type
  WITH NO DATA;


ALTER TABLE public.volume_buyer_3_days_mv OWNER TO root;

--
-- Name: volume_collection_market_user_60_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_market_user_60_days_mv AS
 SELECT t.collection,
    t.market,
    t.maker,
    t.taker,
    t.buyer,
    t.seller,
    t.type,
    sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'UTC'::text) - '60 days'::interval))
  GROUP BY t.collection, t.market, t.maker, t.taker, t.buyer, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_market_user_60_days_mv OWNER TO root;

--
-- Name: volume_buyer_60_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_buyer_60_days_mv AS
 SELECT t.buyer,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_60_days_mv t
  GROUP BY t.buyer, t.type
  WITH NO DATA;


ALTER TABLE public.volume_buyer_60_days_mv OWNER TO root;

--
-- Name: volume_collection_market_user_7_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_market_user_7_days_mv AS
 SELECT t.collection,
    t.market,
    t.maker,
    t.taker,
    t.buyer,
    t.seller,
    t.type,
    sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'UTC'::text) - '7 days'::interval))
  GROUP BY t.collection, t.market, t.maker, t.taker, t.buyer, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_market_user_7_days_mv OWNER TO root;

--
-- Name: volume_buyer_7_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_buyer_7_days_mv AS
 SELECT t.buyer,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_7_days_mv t
  GROUP BY t.buyer, t.type
  WITH NO DATA;


ALTER TABLE public.volume_buyer_7_days_mv OWNER TO root;

--
-- Name: volume_collection_market_user_90_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_market_user_90_days_mv AS
 SELECT t.collection,
    t.market,
    t.maker,
    t.taker,
    t.buyer,
    t.seller,
    t.type,
    sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales
   FROM public.sales_summary t
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'UTC'::text) - '90 days'::interval))
  GROUP BY t.collection, t.market, t.maker, t.taker, t.buyer, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_market_user_90_days_mv OWNER TO root;

--
-- Name: volume_buyer_90_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_buyer_90_days_mv AS
 SELECT t.buyer,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_90_days_mv t
  GROUP BY t.buyer, t.type
  WITH NO DATA;


ALTER TABLE public.volume_buyer_90_days_mv OWNER TO root;

--
-- Name: volume_collection_market_user_before_2024_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_market_user_before_2024_mv AS
 SELECT s.collection,
    s.market,
    s.maker,
    s.taker,
    s.buyer,
    s.seller,
    s.type,
    sum(s.wax_price) AS wax_volume,
    sum(s.usd_price) AS usd_volume,
    count(1) AS sales
   FROM public.sales_summary s
  WHERE (s."timestamp" < '2024-01-01 00:00:00'::timestamp without time zone)
  GROUP BY s.collection, s.market, s.maker, s.taker, s.buyer, s.seller, s.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_market_user_before_2024_mv OWNER TO root;

--
-- Name: volume_collection_buyer_before_2024_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_buyer_before_2024_mv AS
 SELECT volume_collection_market_user_before_2024_mv.collection,
    volume_collection_market_user_before_2024_mv.buyer,
    volume_collection_market_user_before_2024_mv.type,
    sum(volume_collection_market_user_before_2024_mv.wax_volume) AS wax_volume,
    sum(volume_collection_market_user_before_2024_mv.usd_volume) AS usd_volume,
    sum(volume_collection_market_user_before_2024_mv.sales) AS sales
   FROM public.volume_collection_market_user_before_2024_mv
  GROUP BY volume_collection_market_user_before_2024_mv.collection, volume_collection_market_user_before_2024_mv.buyer, volume_collection_market_user_before_2024_mv.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_buyer_before_2024_mv OWNER TO root;

--
-- Name: volume_collection_market_user_from_2024_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_market_user_from_2024_mv AS
 SELECT s.collection,
    s.market,
    s.maker,
    s.taker,
    s.buyer,
    s.seller,
    s.type,
    sum(s.wax_price) AS wax_volume,
    sum(s.usd_price) AS usd_volume,
    count(1) AS sales
   FROM public.sales_summary s
  WHERE (s."timestamp" >= '2024-01-01 00:00:00'::timestamp without time zone)
  GROUP BY s.collection, s.market, s.maker, s.taker, s.buyer, s.seller, s.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_market_user_from_2024_mv OWNER TO root;

--
-- Name: volume_collection_buyer_from_2024_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_buyer_from_2024_mv AS
 SELECT volume_collection_market_user_from_2024_mv.collection,
    volume_collection_market_user_from_2024_mv.buyer,
    volume_collection_market_user_from_2024_mv.type,
    sum(volume_collection_market_user_from_2024_mv.wax_volume) AS wax_volume,
    sum(volume_collection_market_user_from_2024_mv.usd_volume) AS usd_volume,
    sum(volume_collection_market_user_from_2024_mv.sales) AS sales
   FROM public.volume_collection_market_user_from_2024_mv
  GROUP BY volume_collection_market_user_from_2024_mv.collection, volume_collection_market_user_from_2024_mv.buyer, volume_collection_market_user_from_2024_mv.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_buyer_from_2024_mv OWNER TO root;

--
-- Name: volume_collection_buyer_all_time_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_buyer_all_time_mv AS
 SELECT t.collection,
    t.buyer,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM ( SELECT volume_collection_buyer_from_2024_mv.collection,
            volume_collection_buyer_from_2024_mv.buyer,
            volume_collection_buyer_from_2024_mv.type,
            volume_collection_buyer_from_2024_mv.wax_volume,
            volume_collection_buyer_from_2024_mv.usd_volume,
            volume_collection_buyer_from_2024_mv.sales
           FROM public.volume_collection_buyer_from_2024_mv
        UNION ALL
         SELECT volume_collection_buyer_before_2024_mv.collection,
            volume_collection_buyer_before_2024_mv.buyer,
            volume_collection_buyer_before_2024_mv.type,
            volume_collection_buyer_before_2024_mv.wax_volume,
            volume_collection_buyer_before_2024_mv.usd_volume,
            volume_collection_buyer_before_2024_mv.sales
           FROM public.volume_collection_buyer_before_2024_mv) t
  GROUP BY t.collection, t.buyer, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_buyer_all_time_mv OWNER TO root;

--
-- Name: volume_buyer_all_time_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_buyer_all_time_mv AS
 SELECT t.buyer,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_buyer_all_time_mv t
  GROUP BY t.buyer, t.type
  WITH NO DATA;


ALTER TABLE public.volume_buyer_all_time_mv OWNER TO root;

--
-- Name: volume_collection_14_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_14_days_mv AS
 SELECT t.collection,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_14_days_mv t
  GROUP BY t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_14_days_mv OWNER TO root;

--
-- Name: volume_collection_15_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_15_days_mv AS
 SELECT t.collection,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_15_days_mv t
  GROUP BY t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_15_days_mv OWNER TO root;

--
-- Name: volume_collection_180_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_180_days_mv AS
 SELECT t.collection,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_180_days_mv t
  GROUP BY t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_180_days_mv OWNER TO root;

--
-- Name: volume_collection_1_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_1_days_mv AS
 SELECT t.collection,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_1_days_mv t
  GROUP BY t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_1_days_mv OWNER TO root;

--
-- Name: volume_collection_2_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_2_days_mv AS
 SELECT t.collection,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_2_days_mv t
  GROUP BY t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_2_days_mv OWNER TO root;

--
-- Name: volume_collection_30_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_30_days_mv AS
 SELECT t.collection,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_30_days_mv t
  GROUP BY t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_30_days_mv OWNER TO root;

--
-- Name: volume_collection_365_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_365_days_mv AS
 SELECT t.collection,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_365_days_mv t
  GROUP BY t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_365_days_mv OWNER TO root;

--
-- Name: volume_collection_3_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_3_days_mv AS
 SELECT t.collection,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_3_days_mv t
  GROUP BY t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_3_days_mv OWNER TO root;

--
-- Name: volume_collection_60_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_60_days_mv AS
 SELECT t.collection,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_60_days_mv t
  GROUP BY t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_60_days_mv OWNER TO root;

--
-- Name: volume_collection_7_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_7_days_mv AS
 SELECT t.collection,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_7_days_mv t
  GROUP BY t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_7_days_mv OWNER TO root;

--
-- Name: volume_collection_90_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_90_days_mv AS
 SELECT t.collection,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_90_days_mv t
  GROUP BY t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_90_days_mv OWNER TO root;

--
-- Name: volume_collection_market_user_all_time_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_market_user_all_time_mv AS
 SELECT t.collection,
    t.market,
    t.maker,
    t.taker,
    t.buyer,
    t.seller,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM ( SELECT volume_collection_market_user_from_2024_mv.collection,
            volume_collection_market_user_from_2024_mv.market,
            volume_collection_market_user_from_2024_mv.maker,
            volume_collection_market_user_from_2024_mv.taker,
            volume_collection_market_user_from_2024_mv.buyer,
            volume_collection_market_user_from_2024_mv.seller,
            volume_collection_market_user_from_2024_mv.type,
            volume_collection_market_user_from_2024_mv.wax_volume,
            volume_collection_market_user_from_2024_mv.usd_volume,
            volume_collection_market_user_from_2024_mv.sales
           FROM public.volume_collection_market_user_from_2024_mv
        UNION ALL
         SELECT volume_collection_market_user_before_2024_mv.collection,
            volume_collection_market_user_before_2024_mv.market,
            volume_collection_market_user_before_2024_mv.maker,
            volume_collection_market_user_before_2024_mv.taker,
            volume_collection_market_user_before_2024_mv.buyer,
            volume_collection_market_user_before_2024_mv.seller,
            volume_collection_market_user_before_2024_mv.type,
            volume_collection_market_user_before_2024_mv.wax_volume,
            volume_collection_market_user_before_2024_mv.usd_volume,
            volume_collection_market_user_before_2024_mv.sales
           FROM public.volume_collection_market_user_before_2024_mv) t
  GROUP BY t.collection, t.market, t.maker, t.taker, t.buyer, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_market_user_all_time_mv OWNER TO root;

--
-- Name: volume_collection_all_time_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_all_time_mv AS
 SELECT t.collection,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_all_time_mv t
  GROUP BY t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_all_time_mv OWNER TO root;

--
-- Name: volume_collection_buyer_14_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_buyer_14_days_mv AS
 SELECT t.collection,
    t.buyer,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_14_days_mv t
  GROUP BY t.collection, t.buyer, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_buyer_14_days_mv OWNER TO root;

--
-- Name: volume_collection_buyer_15_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_buyer_15_days_mv AS
 SELECT t.collection,
    t.buyer,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_15_days_mv t
  GROUP BY t.collection, t.buyer, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_buyer_15_days_mv OWNER TO root;

--
-- Name: volume_collection_buyer_180_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_buyer_180_days_mv AS
 SELECT t.collection,
    t.buyer,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_180_days_mv t
  GROUP BY t.collection, t.buyer, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_buyer_180_days_mv OWNER TO root;

--
-- Name: volume_collection_buyer_1_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_buyer_1_days_mv AS
 SELECT t.collection,
    t.buyer,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_1_days_mv t
  GROUP BY t.collection, t.buyer, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_buyer_1_days_mv OWNER TO root;

--
-- Name: volume_collection_buyer_2_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_buyer_2_days_mv AS
 SELECT t.collection,
    t.buyer,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_2_days_mv t
  GROUP BY t.collection, t.buyer, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_buyer_2_days_mv OWNER TO root;

--
-- Name: volume_collection_buyer_30_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_buyer_30_days_mv AS
 SELECT t.collection,
    t.buyer,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_30_days_mv t
  GROUP BY t.collection, t.buyer, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_buyer_30_days_mv OWNER TO root;

--
-- Name: volume_collection_buyer_365_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_buyer_365_days_mv AS
 SELECT t.collection,
    t.buyer,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_365_days_mv t
  GROUP BY t.collection, t.buyer, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_buyer_365_days_mv OWNER TO root;

--
-- Name: volume_collection_buyer_3_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_buyer_3_days_mv AS
 SELECT t.collection,
    t.buyer,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_3_days_mv t
  GROUP BY t.collection, t.buyer, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_buyer_3_days_mv OWNER TO root;

--
-- Name: volume_collection_buyer_60_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_buyer_60_days_mv AS
 SELECT t.collection,
    t.buyer,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_60_days_mv t
  GROUP BY t.collection, t.buyer, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_buyer_60_days_mv OWNER TO root;

--
-- Name: volume_collection_buyer_7_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_buyer_7_days_mv AS
 SELECT t.collection,
    t.buyer,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_7_days_mv t
  GROUP BY t.collection, t.buyer, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_buyer_7_days_mv OWNER TO root;

--
-- Name: volume_collection_buyer_90_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_buyer_90_days_mv AS
 SELECT t.collection,
    t.buyer,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_90_days_mv t
  GROUP BY t.collection, t.buyer, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_buyer_90_days_mv OWNER TO root;

--
-- Name: volume_collection_market_14_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_market_14_days_mv AS
 SELECT t.collection,
    t.market,
    t.maker,
    t.taker,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_14_days_mv t
  GROUP BY t.collection, t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_market_14_days_mv OWNER TO root;

--
-- Name: volume_collection_market_15_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_market_15_days_mv AS
 SELECT t.collection,
    t.market,
    t.maker,
    t.taker,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_15_days_mv t
  GROUP BY t.collection, t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_market_15_days_mv OWNER TO root;

--
-- Name: volume_collection_market_180_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_market_180_days_mv AS
 SELECT t.collection,
    t.market,
    t.maker,
    t.taker,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_180_days_mv t
  GROUP BY t.collection, t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_market_180_days_mv OWNER TO root;

--
-- Name: volume_collection_market_1_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_market_1_days_mv AS
 SELECT t.collection,
    t.market,
    t.maker,
    t.taker,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_1_days_mv t
  GROUP BY t.collection, t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_market_1_days_mv OWNER TO root;

--
-- Name: volume_collection_market_2_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_market_2_days_mv AS
 SELECT t.collection,
    t.market,
    t.maker,
    t.taker,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_2_days_mv t
  GROUP BY t.collection, t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_market_2_days_mv OWNER TO root;

--
-- Name: volume_collection_market_30_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_market_30_days_mv AS
 SELECT t.collection,
    t.market,
    t.maker,
    t.taker,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_30_days_mv t
  GROUP BY t.collection, t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_market_30_days_mv OWNER TO root;

--
-- Name: volume_collection_market_365_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_market_365_days_mv AS
 SELECT t.collection,
    t.market,
    t.maker,
    t.taker,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_365_days_mv t
  GROUP BY t.collection, t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_market_365_days_mv OWNER TO root;

--
-- Name: volume_collection_market_3_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_market_3_days_mv AS
 SELECT t.collection,
    t.market,
    t.maker,
    t.taker,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_3_days_mv t
  GROUP BY t.collection, t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_market_3_days_mv OWNER TO root;

--
-- Name: volume_collection_market_60_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_market_60_days_mv AS
 SELECT t.collection,
    t.market,
    t.maker,
    t.taker,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_60_days_mv t
  GROUP BY t.collection, t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_market_60_days_mv OWNER TO root;

--
-- Name: volume_collection_market_7_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_market_7_days_mv AS
 SELECT t.collection,
    t.market,
    t.maker,
    t.taker,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_7_days_mv t
  GROUP BY t.collection, t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_market_7_days_mv OWNER TO root;

--
-- Name: volume_collection_market_90_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_market_90_days_mv AS
 SELECT t.collection,
    t.market,
    t.maker,
    t.taker,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_90_days_mv t
  GROUP BY t.collection, t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_market_90_days_mv OWNER TO root;

--
-- Name: volume_collection_market_all_time_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_market_all_time_mv AS
 SELECT t.collection,
    t.market,
    t.maker,
    t.taker,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_all_time_mv t
  GROUP BY t.collection, t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_market_all_time_mv OWNER TO root;

--
-- Name: volume_collection_seller_14_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_seller_14_days_mv AS
 SELECT t.collection,
    t.seller,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_14_days_mv t
  GROUP BY t.collection, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_seller_14_days_mv OWNER TO root;

--
-- Name: volume_collection_seller_15_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_seller_15_days_mv AS
 SELECT t.collection,
    t.seller,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_15_days_mv t
  GROUP BY t.collection, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_seller_15_days_mv OWNER TO root;

--
-- Name: volume_collection_seller_180_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_seller_180_days_mv AS
 SELECT t.collection,
    t.seller,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_180_days_mv t
  GROUP BY t.collection, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_seller_180_days_mv OWNER TO root;

--
-- Name: volume_collection_seller_1_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_seller_1_days_mv AS
 SELECT t.collection,
    t.seller,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_1_days_mv t
  GROUP BY t.collection, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_seller_1_days_mv OWNER TO root;

--
-- Name: volume_collection_seller_2_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_seller_2_days_mv AS
 SELECT t.collection,
    t.seller,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_2_days_mv t
  GROUP BY t.collection, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_seller_2_days_mv OWNER TO root;

--
-- Name: volume_collection_seller_30_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_seller_30_days_mv AS
 SELECT t.collection,
    t.seller,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_30_days_mv t
  GROUP BY t.collection, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_seller_30_days_mv OWNER TO root;

--
-- Name: volume_collection_seller_365_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_seller_365_days_mv AS
 SELECT t.collection,
    t.seller,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_365_days_mv t
  GROUP BY t.collection, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_seller_365_days_mv OWNER TO root;

--
-- Name: volume_collection_seller_3_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_seller_3_days_mv AS
 SELECT t.collection,
    t.seller,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_3_days_mv t
  GROUP BY t.collection, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_seller_3_days_mv OWNER TO root;

--
-- Name: volume_collection_seller_60_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_seller_60_days_mv AS
 SELECT t.collection,
    t.seller,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_60_days_mv t
  GROUP BY t.collection, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_seller_60_days_mv OWNER TO root;

--
-- Name: volume_collection_seller_7_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_seller_7_days_mv AS
 SELECT t.collection,
    t.seller,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_7_days_mv t
  GROUP BY t.collection, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_seller_7_days_mv OWNER TO root;

--
-- Name: volume_collection_seller_90_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_seller_90_days_mv AS
 SELECT t.collection,
    t.seller,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_90_days_mv t
  GROUP BY t.collection, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_seller_90_days_mv OWNER TO root;

--
-- Name: volume_collection_seller_before_2024_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_seller_before_2024_mv AS
 SELECT volume_collection_market_user_before_2024_mv.collection,
    volume_collection_market_user_before_2024_mv.seller,
    volume_collection_market_user_before_2024_mv.type,
    sum(volume_collection_market_user_before_2024_mv.wax_volume) AS wax_volume,
    sum(volume_collection_market_user_before_2024_mv.usd_volume) AS usd_volume,
    sum(volume_collection_market_user_before_2024_mv.sales) AS sales
   FROM public.volume_collection_market_user_before_2024_mv
  GROUP BY volume_collection_market_user_before_2024_mv.collection, volume_collection_market_user_before_2024_mv.seller, volume_collection_market_user_before_2024_mv.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_seller_before_2024_mv OWNER TO root;

--
-- Name: volume_collection_seller_from_2024_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_seller_from_2024_mv AS
 SELECT volume_collection_market_user_from_2024_mv.collection,
    volume_collection_market_user_from_2024_mv.seller,
    volume_collection_market_user_from_2024_mv.type,
    sum(volume_collection_market_user_from_2024_mv.wax_volume) AS wax_volume,
    sum(volume_collection_market_user_from_2024_mv.usd_volume) AS usd_volume,
    sum(volume_collection_market_user_from_2024_mv.sales) AS sales
   FROM public.volume_collection_market_user_from_2024_mv
  GROUP BY volume_collection_market_user_from_2024_mv.collection, volume_collection_market_user_from_2024_mv.seller, volume_collection_market_user_from_2024_mv.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_seller_from_2024_mv OWNER TO root;

--
-- Name: volume_collection_seller_all_time_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_collection_seller_all_time_mv AS
 SELECT t.collection,
    t.seller,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM ( SELECT volume_collection_seller_from_2024_mv.collection,
            volume_collection_seller_from_2024_mv.seller,
            volume_collection_seller_from_2024_mv.type,
            volume_collection_seller_from_2024_mv.wax_volume,
            volume_collection_seller_from_2024_mv.usd_volume,
            volume_collection_seller_from_2024_mv.sales
           FROM public.volume_collection_seller_from_2024_mv
        UNION ALL
         SELECT volume_collection_seller_before_2024_mv.collection,
            volume_collection_seller_before_2024_mv.seller,
            volume_collection_seller_before_2024_mv.type,
            volume_collection_seller_before_2024_mv.wax_volume,
            volume_collection_seller_before_2024_mv.usd_volume,
            volume_collection_seller_before_2024_mv.sales
           FROM public.volume_collection_seller_before_2024_mv) t
  GROUP BY t.collection, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_collection_seller_all_time_mv OWNER TO root;

--
-- Name: volume_drop_14_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.volume_drop_14_days_mv AS
 SELECT sales_summary.collection,
    sales_summary.listing_id AS drop_id,
    sales_summary.market,
    sum(sales_summary.wax_price) AS wax_volume,
    sum(sales_summary.usd_price) AS usd_volume,
    sum(sales_summary.num_items) AS sales,
    count(DISTINCT sales_summary.buyer) AS buyers
   FROM public.sales_summary
  WHERE (((sales_summary.type)::text = 'drops'::text) AND (sales_summary."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '14 days'::interval)))
  GROUP BY sales_summary.collection, sales_summary.listing_id, sales_summary.market
  WITH NO DATA;


ALTER TABLE public.volume_drop_14_days_mv OWNER TO postgres;

--
-- Name: volume_drop_15_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.volume_drop_15_days_mv AS
 SELECT sales_summary.collection,
    sales_summary.listing_id AS drop_id,
    sales_summary.market,
    sum(sales_summary.wax_price) AS wax_volume,
    sum(sales_summary.usd_price) AS usd_volume,
    sum(sales_summary.num_items) AS sales,
    count(DISTINCT sales_summary.buyer) AS buyers
   FROM public.sales_summary
  WHERE (((sales_summary.type)::text = 'drops'::text) AND (sales_summary."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '15 days'::interval)))
  GROUP BY sales_summary.collection, sales_summary.listing_id, sales_summary.market
  WITH NO DATA;


ALTER TABLE public.volume_drop_15_days_mv OWNER TO postgres;

--
-- Name: volume_drop_180_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.volume_drop_180_days_mv AS
 SELECT sales_summary.collection,
    sales_summary.listing_id AS drop_id,
    sales_summary.market,
    sum(sales_summary.wax_price) AS wax_volume,
    sum(sales_summary.usd_price) AS usd_volume,
    sum(sales_summary.num_items) AS sales,
    count(DISTINCT sales_summary.buyer) AS buyers
   FROM public.sales_summary
  WHERE (((sales_summary.type)::text = 'drops'::text) AND (sales_summary."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '180 days'::interval)))
  GROUP BY sales_summary.collection, sales_summary.listing_id, sales_summary.market
  WITH NO DATA;


ALTER TABLE public.volume_drop_180_days_mv OWNER TO postgres;

--
-- Name: volume_drop_1_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.volume_drop_1_days_mv AS
 SELECT sales_summary.collection,
    sales_summary.listing_id AS drop_id,
    sales_summary.market,
    sum(sales_summary.wax_price) AS wax_volume,
    sum(sales_summary.usd_price) AS usd_volume,
    sum(sales_summary.num_items) AS sales,
    count(DISTINCT sales_summary.buyer) AS buyers
   FROM public.sales_summary
  WHERE (((sales_summary.type)::text = 'drops'::text) AND (sales_summary."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '1 day'::interval)))
  GROUP BY sales_summary.collection, sales_summary.listing_id, sales_summary.market
  WITH NO DATA;


ALTER TABLE public.volume_drop_1_days_mv OWNER TO postgres;

--
-- Name: volume_drop_2_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.volume_drop_2_days_mv AS
 SELECT sales_summary.collection,
    sales_summary.listing_id AS drop_id,
    sales_summary.market,
    sum(sales_summary.wax_price) AS wax_volume,
    sum(sales_summary.usd_price) AS usd_volume,
    sum(sales_summary.num_items) AS sales,
    count(DISTINCT sales_summary.buyer) AS buyers
   FROM public.sales_summary
  WHERE (((sales_summary.type)::text = 'drops'::text) AND (sales_summary."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '2 days'::interval)))
  GROUP BY sales_summary.collection, sales_summary.listing_id, sales_summary.market
  WITH NO DATA;


ALTER TABLE public.volume_drop_2_days_mv OWNER TO postgres;

--
-- Name: volume_drop_30_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.volume_drop_30_days_mv AS
 SELECT sales_summary.collection,
    sales_summary.listing_id AS drop_id,
    sales_summary.market,
    sum(sales_summary.wax_price) AS wax_volume,
    sum(sales_summary.usd_price) AS usd_volume,
    sum(sales_summary.num_items) AS sales,
    count(DISTINCT sales_summary.buyer) AS buyers
   FROM public.sales_summary
  WHERE (((sales_summary.type)::text = 'drops'::text) AND (sales_summary."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '30 days'::interval)))
  GROUP BY sales_summary.collection, sales_summary.listing_id, sales_summary.market
  WITH NO DATA;


ALTER TABLE public.volume_drop_30_days_mv OWNER TO postgres;

--
-- Name: volume_drop_365_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.volume_drop_365_days_mv AS
 SELECT sales_summary.collection,
    sales_summary.listing_id AS drop_id,
    sales_summary.market,
    sum(sales_summary.wax_price) AS wax_volume,
    sum(sales_summary.usd_price) AS usd_volume,
    sum(sales_summary.num_items) AS sales,
    count(DISTINCT sales_summary.buyer) AS buyers
   FROM public.sales_summary
  WHERE (((sales_summary.type)::text = 'drops'::text) AND (sales_summary."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '365 days'::interval)))
  GROUP BY sales_summary.collection, sales_summary.listing_id, sales_summary.market
  WITH NO DATA;


ALTER TABLE public.volume_drop_365_days_mv OWNER TO postgres;

--
-- Name: volume_drop_3_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.volume_drop_3_days_mv AS
 SELECT sales_summary.collection,
    sales_summary.listing_id AS drop_id,
    sales_summary.market,
    sum(sales_summary.wax_price) AS wax_volume,
    sum(sales_summary.usd_price) AS usd_volume,
    sum(sales_summary.num_items) AS sales,
    count(DISTINCT sales_summary.buyer) AS buyers
   FROM public.sales_summary
  WHERE (((sales_summary.type)::text = 'drops'::text) AND (sales_summary."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '3 days'::interval)))
  GROUP BY sales_summary.collection, sales_summary.listing_id, sales_summary.market
  WITH NO DATA;


ALTER TABLE public.volume_drop_3_days_mv OWNER TO postgres;

--
-- Name: volume_drop_60_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.volume_drop_60_days_mv AS
 SELECT sales_summary.collection,
    sales_summary.listing_id AS drop_id,
    sales_summary.market,
    sum(sales_summary.wax_price) AS wax_volume,
    sum(sales_summary.usd_price) AS usd_volume,
    sum(sales_summary.num_items) AS sales,
    count(DISTINCT sales_summary.buyer) AS buyers
   FROM public.sales_summary
  WHERE (((sales_summary.type)::text = 'drops'::text) AND (sales_summary."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '60 days'::interval)))
  GROUP BY sales_summary.collection, sales_summary.listing_id, sales_summary.market
  WITH NO DATA;


ALTER TABLE public.volume_drop_60_days_mv OWNER TO postgres;

--
-- Name: volume_drop_7_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.volume_drop_7_days_mv AS
 SELECT sales_summary.collection,
    sales_summary.listing_id AS drop_id,
    sales_summary.market,
    sum(sales_summary.wax_price) AS wax_volume,
    sum(sales_summary.usd_price) AS usd_volume,
    sum(sales_summary.num_items) AS sales,
    count(DISTINCT sales_summary.buyer) AS buyers
   FROM public.sales_summary
  WHERE (((sales_summary.type)::text = 'drops'::text) AND (sales_summary."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '7 days'::interval)))
  GROUP BY sales_summary.collection, sales_summary.listing_id, sales_summary.market
  WITH NO DATA;


ALTER TABLE public.volume_drop_7_days_mv OWNER TO postgres;

--
-- Name: volume_drop_90_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.volume_drop_90_days_mv AS
 SELECT sales_summary.collection,
    sales_summary.listing_id AS drop_id,
    sales_summary.market,
    sum(sales_summary.wax_price) AS wax_volume,
    sum(sales_summary.usd_price) AS usd_volume,
    sum(sales_summary.num_items) AS sales,
    count(DISTINCT sales_summary.buyer) AS buyers
   FROM public.sales_summary
  WHERE (((sales_summary.type)::text = 'drops'::text) AND (sales_summary."timestamp" > ((now() AT TIME ZONE 'utc'::text) - '90 days'::interval)))
  GROUP BY sales_summary.collection, sales_summary.listing_id, sales_summary.market
  WITH NO DATA;


ALTER TABLE public.volume_drop_90_days_mv OWNER TO postgres;

--
-- Name: volume_drop_all_time_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.volume_drop_all_time_mv AS
 SELECT sales_summary.collection,
    sales_summary.listing_id AS drop_id,
    sales_summary.market,
    sum(sales_summary.wax_price) AS wax_volume,
    sum(sales_summary.usd_price) AS usd_volume,
    sum(sales_summary.num_items) AS sales,
    count(DISTINCT sales_summary.buyer) AS buyers
   FROM public.sales_summary
  WHERE ((sales_summary.type)::text = 'drops'::text)
  GROUP BY sales_summary.collection, sales_summary.listing_id, sales_summary.market
  WITH NO DATA;


ALTER TABLE public.volume_drop_all_time_mv OWNER TO postgres;

--
-- Name: volume_market_14_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_market_14_days_mv AS
 SELECT t.market,
    t.maker,
    t.taker,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_14_days_mv t
  GROUP BY t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.volume_market_14_days_mv OWNER TO root;

--
-- Name: volume_market_15_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_market_15_days_mv AS
 SELECT t.market,
    t.maker,
    t.taker,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_15_days_mv t
  GROUP BY t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.volume_market_15_days_mv OWNER TO root;

--
-- Name: volume_market_180_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_market_180_days_mv AS
 SELECT t.market,
    t.maker,
    t.taker,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_180_days_mv t
  GROUP BY t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.volume_market_180_days_mv OWNER TO root;

--
-- Name: volume_market_1_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_market_1_days_mv AS
 SELECT t.market,
    t.maker,
    t.taker,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_1_days_mv t
  GROUP BY t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.volume_market_1_days_mv OWNER TO root;

--
-- Name: volume_market_2_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_market_2_days_mv AS
 SELECT t.market,
    t.maker,
    t.taker,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_2_days_mv t
  GROUP BY t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.volume_market_2_days_mv OWNER TO root;

--
-- Name: volume_market_30_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_market_30_days_mv AS
 SELECT t.market,
    t.maker,
    t.taker,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_30_days_mv t
  GROUP BY t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.volume_market_30_days_mv OWNER TO root;

--
-- Name: volume_market_365_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_market_365_days_mv AS
 SELECT t.market,
    t.maker,
    t.taker,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_365_days_mv t
  GROUP BY t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.volume_market_365_days_mv OWNER TO root;

--
-- Name: volume_market_3_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_market_3_days_mv AS
 SELECT t.market,
    t.maker,
    t.taker,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_3_days_mv t
  GROUP BY t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.volume_market_3_days_mv OWNER TO root;

--
-- Name: volume_market_60_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_market_60_days_mv AS
 SELECT t.market,
    t.maker,
    t.taker,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_60_days_mv t
  GROUP BY t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.volume_market_60_days_mv OWNER TO root;

--
-- Name: volume_market_7_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_market_7_days_mv AS
 SELECT t.market,
    t.maker,
    t.taker,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_7_days_mv t
  GROUP BY t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.volume_market_7_days_mv OWNER TO root;

--
-- Name: volume_market_90_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_market_90_days_mv AS
 SELECT t.market,
    t.maker,
    t.taker,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_90_days_mv t
  GROUP BY t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.volume_market_90_days_mv OWNER TO root;

--
-- Name: volume_market_all_time_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_market_all_time_mv AS
 SELECT t.market,
    t.maker,
    t.taker,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_collection_market_user_all_time_mv t
  GROUP BY t.market, t.maker, t.taker, t.type
  WITH NO DATA;


ALTER TABLE public.volume_market_all_time_mv OWNER TO root;

--
-- Name: volume_seller_14_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_seller_14_days_mv AS
 SELECT t.seller,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_14_days_mv t
  GROUP BY t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_seller_14_days_mv OWNER TO root;

--
-- Name: volume_seller_15_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_seller_15_days_mv AS
 SELECT t.seller,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_15_days_mv t
  GROUP BY t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_seller_15_days_mv OWNER TO root;

--
-- Name: volume_seller_180_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_seller_180_days_mv AS
 SELECT t.seller,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_180_days_mv t
  GROUP BY t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_seller_180_days_mv OWNER TO root;

--
-- Name: volume_seller_1_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_seller_1_days_mv AS
 SELECT t.seller,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_1_days_mv t
  GROUP BY t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_seller_1_days_mv OWNER TO root;

--
-- Name: volume_seller_2_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_seller_2_days_mv AS
 SELECT t.seller,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_2_days_mv t
  GROUP BY t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_seller_2_days_mv OWNER TO root;

--
-- Name: volume_seller_30_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_seller_30_days_mv AS
 SELECT t.seller,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_30_days_mv t
  GROUP BY t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_seller_30_days_mv OWNER TO root;

--
-- Name: volume_seller_365_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_seller_365_days_mv AS
 SELECT t.seller,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_365_days_mv t
  GROUP BY t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_seller_365_days_mv OWNER TO root;

--
-- Name: volume_seller_3_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_seller_3_days_mv AS
 SELECT t.seller,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_3_days_mv t
  GROUP BY t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_seller_3_days_mv OWNER TO root;

--
-- Name: volume_seller_60_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_seller_60_days_mv AS
 SELECT t.seller,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_60_days_mv t
  GROUP BY t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_seller_60_days_mv OWNER TO root;

--
-- Name: volume_seller_7_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_seller_7_days_mv AS
 SELECT t.seller,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_7_days_mv t
  GROUP BY t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_seller_7_days_mv OWNER TO root;

--
-- Name: volume_seller_90_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_seller_90_days_mv AS
 SELECT t.seller,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_market_user_90_days_mv t
  GROUP BY t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_seller_90_days_mv OWNER TO root;

--
-- Name: volume_seller_all_time_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_seller_all_time_mv AS
 SELECT t.seller,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM public.volume_collection_seller_all_time_mv t
  GROUP BY t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_seller_all_time_mv OWNER TO root;

--
-- Name: volume_template_user_14_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_template_user_14_days_mv AS
 SELECT t.template_id,
    t.schema,
    t.collection,
    s.buyer,
    s.seller,
    s.type,
    sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales
   FROM (public.template_sales t
     JOIN public.sales_summary s USING (seq))
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'UTC'::text) - '14 days'::interval))
  GROUP BY t.template_id, t.schema, t.collection, s.buyer, s.seller, s.type
  WITH NO DATA;


ALTER TABLE public.volume_template_user_14_days_mv OWNER TO root;

--
-- Name: volume_template_14_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_template_14_days_mv AS
 SELECT t.template_id,
    t.schema,
    t.collection,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_template_user_14_days_mv t
  GROUP BY t.template_id, t.schema, t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.volume_template_14_days_mv OWNER TO root;

--
-- Name: volume_template_user_15_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_template_user_15_days_mv AS
 SELECT t.template_id,
    t.schema,
    t.collection,
    s.buyer,
    s.seller,
    s.type,
    sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales
   FROM (public.template_sales t
     JOIN public.sales_summary s USING (seq))
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'UTC'::text) - '15 days'::interval))
  GROUP BY t.template_id, t.schema, t.collection, s.buyer, s.seller, s.type
  WITH NO DATA;


ALTER TABLE public.volume_template_user_15_days_mv OWNER TO root;

--
-- Name: volume_template_15_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_template_15_days_mv AS
 SELECT t.template_id,
    t.schema,
    t.collection,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_template_user_15_days_mv t
  GROUP BY t.template_id, t.schema, t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.volume_template_15_days_mv OWNER TO root;

--
-- Name: volume_template_user_180_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_template_user_180_days_mv AS
 SELECT t.template_id,
    t.schema,
    t.collection,
    s.buyer,
    s.seller,
    s.type,
    sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales
   FROM (public.template_sales t
     JOIN public.sales_summary s USING (seq))
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'UTC'::text) - '180 days'::interval))
  GROUP BY t.template_id, t.schema, t.collection, s.buyer, s.seller, s.type
  WITH NO DATA;


ALTER TABLE public.volume_template_user_180_days_mv OWNER TO root;

--
-- Name: volume_template_180_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_template_180_days_mv AS
 SELECT t.template_id,
    t.schema,
    t.collection,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_template_user_180_days_mv t
  GROUP BY t.template_id, t.schema, t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.volume_template_180_days_mv OWNER TO root;

--
-- Name: volume_template_user_1_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_template_user_1_days_mv AS
 SELECT t.template_id,
    t.schema,
    t.collection,
    s.buyer,
    s.seller,
    s.type,
    sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales
   FROM (public.template_sales t
     JOIN public.sales_summary s USING (seq))
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'UTC'::text) - '1 day'::interval))
  GROUP BY t.template_id, t.schema, t.collection, s.buyer, s.seller, s.type
  WITH NO DATA;


ALTER TABLE public.volume_template_user_1_days_mv OWNER TO root;

--
-- Name: volume_template_1_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_template_1_days_mv AS
 SELECT t.template_id,
    t.schema,
    t.collection,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_template_user_1_days_mv t
  GROUP BY t.template_id, t.schema, t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.volume_template_1_days_mv OWNER TO root;

--
-- Name: volume_template_user_2_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_template_user_2_days_mv AS
 SELECT t.template_id,
    t.schema,
    t.collection,
    s.buyer,
    s.seller,
    s.type,
    sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales
   FROM (public.template_sales t
     JOIN public.sales_summary s USING (seq))
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'UTC'::text) - '2 days'::interval))
  GROUP BY t.template_id, t.schema, t.collection, s.buyer, s.seller, s.type
  WITH NO DATA;


ALTER TABLE public.volume_template_user_2_days_mv OWNER TO root;

--
-- Name: volume_template_2_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_template_2_days_mv AS
 SELECT t.template_id,
    t.schema,
    t.collection,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_template_user_2_days_mv t
  GROUP BY t.template_id, t.schema, t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.volume_template_2_days_mv OWNER TO root;

--
-- Name: volume_template_user_30_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_template_user_30_days_mv AS
 SELECT t.template_id,
    t.schema,
    t.collection,
    s.buyer,
    s.seller,
    s.type,
    sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales
   FROM (public.template_sales t
     JOIN public.sales_summary s USING (seq))
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'UTC'::text) - '30 days'::interval))
  GROUP BY t.template_id, t.schema, t.collection, s.buyer, s.seller, s.type
  WITH NO DATA;


ALTER TABLE public.volume_template_user_30_days_mv OWNER TO root;

--
-- Name: volume_template_30_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_template_30_days_mv AS
 SELECT t.template_id,
    t.schema,
    t.collection,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_template_user_30_days_mv t
  GROUP BY t.template_id, t.schema, t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.volume_template_30_days_mv OWNER TO root;

--
-- Name: volume_template_user_365_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_template_user_365_days_mv AS
 SELECT t.template_id,
    t.schema,
    t.collection,
    s.buyer,
    s.seller,
    s.type,
    sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales
   FROM (public.template_sales t
     JOIN public.sales_summary s USING (seq))
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'UTC'::text) - '365 days'::interval))
  GROUP BY t.template_id, t.schema, t.collection, s.buyer, s.seller, s.type
  WITH NO DATA;


ALTER TABLE public.volume_template_user_365_days_mv OWNER TO root;

--
-- Name: volume_template_365_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_template_365_days_mv AS
 SELECT t.template_id,
    t.schema,
    t.collection,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_template_user_365_days_mv t
  GROUP BY t.template_id, t.schema, t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.volume_template_365_days_mv OWNER TO root;

--
-- Name: volume_template_user_3_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_template_user_3_days_mv AS
 SELECT t.template_id,
    t.schema,
    t.collection,
    s.buyer,
    s.seller,
    s.type,
    sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales
   FROM (public.template_sales t
     JOIN public.sales_summary s USING (seq))
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'UTC'::text) - '3 days'::interval))
  GROUP BY t.template_id, t.schema, t.collection, s.buyer, s.seller, s.type
  WITH NO DATA;


ALTER TABLE public.volume_template_user_3_days_mv OWNER TO root;

--
-- Name: volume_template_3_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_template_3_days_mv AS
 SELECT t.template_id,
    t.schema,
    t.collection,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_template_user_3_days_mv t
  GROUP BY t.template_id, t.schema, t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.volume_template_3_days_mv OWNER TO root;

--
-- Name: volume_template_user_60_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_template_user_60_days_mv AS
 SELECT t.template_id,
    t.schema,
    t.collection,
    s.buyer,
    s.seller,
    s.type,
    sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales
   FROM (public.template_sales t
     JOIN public.sales_summary s USING (seq))
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'UTC'::text) - '60 days'::interval))
  GROUP BY t.template_id, t.schema, t.collection, s.buyer, s.seller, s.type
  WITH NO DATA;


ALTER TABLE public.volume_template_user_60_days_mv OWNER TO root;

--
-- Name: volume_template_60_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_template_60_days_mv AS
 SELECT t.template_id,
    t.schema,
    t.collection,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_template_user_60_days_mv t
  GROUP BY t.template_id, t.schema, t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.volume_template_60_days_mv OWNER TO root;

--
-- Name: volume_template_user_7_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_template_user_7_days_mv AS
 SELECT t.template_id,
    t.schema,
    t.collection,
    s.buyer,
    s.seller,
    s.type,
    sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales
   FROM (public.template_sales t
     JOIN public.sales_summary s USING (seq))
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'UTC'::text) - '7 days'::interval))
  GROUP BY t.template_id, t.schema, t.collection, s.buyer, s.seller, s.type
  WITH NO DATA;


ALTER TABLE public.volume_template_user_7_days_mv OWNER TO root;

--
-- Name: volume_template_7_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_template_7_days_mv AS
 SELECT t.template_id,
    t.schema,
    t.collection,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_template_user_7_days_mv t
  GROUP BY t.template_id, t.schema, t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.volume_template_7_days_mv OWNER TO root;

--
-- Name: volume_template_user_90_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_template_user_90_days_mv AS
 SELECT t.template_id,
    t.schema,
    t.collection,
    s.buyer,
    s.seller,
    s.type,
    sum(t.wax_price) AS wax_volume,
    sum(t.usd_price) AS usd_volume,
    count(1) AS sales
   FROM (public.template_sales t
     JOIN public.sales_summary s USING (seq))
  WHERE (t."timestamp" > ((now() AT TIME ZONE 'UTC'::text) - '90 days'::interval))
  GROUP BY t.template_id, t.schema, t.collection, s.buyer, s.seller, s.type
  WITH NO DATA;


ALTER TABLE public.volume_template_user_90_days_mv OWNER TO root;

--
-- Name: volume_template_90_days_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_template_90_days_mv AS
 SELECT t.template_id,
    t.schema,
    t.collection,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_template_user_90_days_mv t
  GROUP BY t.template_id, t.schema, t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.volume_template_90_days_mv OWNER TO root;

--
-- Name: volume_template_user_before_2024_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_template_user_before_2024_mv AS
 SELECT t.template_id,
    t.schema,
    t.collection,
    s.buyer,
    s.seller,
    s.type,
    sum(s.wax_price) AS wax_volume,
    sum(s.usd_price) AS usd_volume,
    count(1) AS sales
   FROM (public.template_sales t
     LEFT JOIN public.sales_summary s USING (seq))
  WHERE (s."timestamp" < '2024-01-01 00:00:00'::timestamp without time zone)
  GROUP BY t.template_id, t.schema, t.collection, s.buyer, s.seller, s.type
  WITH NO DATA;


ALTER TABLE public.volume_template_user_before_2024_mv OWNER TO root;

--
-- Name: volume_template_user_from_2024_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_template_user_from_2024_mv AS
 SELECT t.template_id,
    t.schema,
    t.collection,
    s.buyer,
    s.seller,
    s.type,
    sum(s.wax_price) AS wax_volume,
    sum(s.usd_price) AS usd_volume,
    count(1) AS sales
   FROM (public.template_sales t
     LEFT JOIN public.sales_summary s USING (seq))
  WHERE (s."timestamp" >= '2024-01-01 00:00:00'::timestamp without time zone)
  GROUP BY t.template_id, t.schema, t.collection, s.buyer, s.seller, s.type
  WITH NO DATA;


ALTER TABLE public.volume_template_user_from_2024_mv OWNER TO root;

--
-- Name: volume_template_user_all_time_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_template_user_all_time_mv AS
 SELECT t.template_id,
    t.schema,
    t.collection,
    t.buyer,
    t.seller,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales
   FROM ( SELECT volume_template_user_from_2024_mv.template_id,
            volume_template_user_from_2024_mv.schema,
            volume_template_user_from_2024_mv.collection,
            volume_template_user_from_2024_mv.buyer,
            volume_template_user_from_2024_mv.seller,
            volume_template_user_from_2024_mv.type,
            volume_template_user_from_2024_mv.wax_volume,
            volume_template_user_from_2024_mv.usd_volume,
            volume_template_user_from_2024_mv.sales
           FROM public.volume_template_user_from_2024_mv
        UNION ALL
         SELECT volume_template_user_before_2024_mv.template_id,
            volume_template_user_before_2024_mv.schema,
            volume_template_user_before_2024_mv.collection,
            volume_template_user_before_2024_mv.buyer,
            volume_template_user_before_2024_mv.seller,
            volume_template_user_before_2024_mv.type,
            volume_template_user_before_2024_mv.wax_volume,
            volume_template_user_before_2024_mv.usd_volume,
            volume_template_user_before_2024_mv.sales
           FROM public.volume_template_user_before_2024_mv) t
  GROUP BY t.template_id, t.schema, t.collection, t.buyer, t.seller, t.type
  WITH NO DATA;


ALTER TABLE public.volume_template_user_all_time_mv OWNER TO root;

--
-- Name: volume_template_all_time_mv; Type: MATERIALIZED VIEW; Schema: public; Owner: root
--

CREATE MATERIALIZED VIEW public.volume_template_all_time_mv AS
 SELECT t.template_id,
    t.schema,
    t.collection,
    t.type,
    sum(t.wax_volume) AS wax_volume,
    sum(t.usd_volume) AS usd_volume,
    sum(t.sales) AS sales,
    count(DISTINCT t.seller) AS sellers,
    count(DISTINCT t.buyer) AS buyers
   FROM public.volume_template_user_all_time_mv t
  GROUP BY t.template_id, t.schema, t.collection, t.type
  WITH NO DATA;


ALTER TABLE public.volume_template_all_time_mv OWNER TO root;

--
-- Name: whitelist_overwrite; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.whitelist_overwrite (
    collection character varying(13)
);


ALTER TABLE public.whitelist_overwrite OWNER TO postgres;

--
-- Name: wuffi_airdrop_claimers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.wuffi_airdrop_claimers (
    airdrop_id bigint,
    claimer character varying(13),
    tokens character varying(64),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.wuffi_airdrop_claimers OWNER TO postgres;

--
-- Name: wuffi_airdrop_claims; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.wuffi_airdrop_claims (
    airdrop_id bigint,
    account character varying(13),
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.wuffi_airdrop_claims OWNER TO postgres;

--
-- Name: wuffi_airdrop_data_updates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.wuffi_airdrop_data_updates (
    airdrop_id bigint,
    display_data text,
    old_display_data text,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.wuffi_airdrop_data_updates OWNER TO postgres;

--
-- Name: wuffi_airdrop_ready_updates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.wuffi_airdrop_ready_updates (
    airdrop_id bigint,
    ready boolean,
    old_ready boolean,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.wuffi_airdrop_ready_updates OWNER TO postgres;

--
-- Name: wuffi_airdrops; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.wuffi_airdrops (
    airdrop_id bigint,
    token character varying(64),
    contract character varying(13),
    creator character varying(13),
    holder_contract character varying(13),
    min_amount character varying(64),
    max_amount character varying(64),
    snapshot_time timestamp without time zone,
    display_data text,
    ready boolean,
    seq bigint,
    block_num bigint,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.wuffi_airdrops OWNER TO postgres;

--
-- Name: attributes attribute_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attributes ALTER COLUMN attribute_id SET DEFAULT nextval('public.attributes_attribute_id_seq'::regclass);


--
-- Name: data data_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data ALTER COLUMN data_id SET DEFAULT nextval('public.data_data_id_seq'::regclass);


--
-- Name: images image_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.images ALTER COLUMN image_id SET DEFAULT nextval('public.images_image_id_seq'::regclass);


--
-- Name: listings sale_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.listings ALTER COLUMN sale_id SET DEFAULT nextval('public.listings_sale_id_seq'::regclass);


--
-- Name: memos memo_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.memos ALTER COLUMN memo_id SET DEFAULT nextval('public.memos_memo_id_seq'::regclass);


--
-- Name: names name_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.names ALTER COLUMN name_id SET DEFAULT nextval('public.names_name_id_seq'::regclass);


--
-- Name: sets set_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sets ALTER COLUMN set_id SET DEFAULT nextval('public.sets_set_id_seq'::regclass);


--
-- Name: tags tag_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tags ALTER COLUMN tag_id SET DEFAULT nextval('public.tags_tag_id_seq'::regclass);


--
-- Name: transaction_ids transaction_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transaction_ids ALTER COLUMN transaction_id SET DEFAULT nextval('public.transaction_ids_transaction_id_seq'::regclass);


--
-- Name: transactions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions ALTER COLUMN id SET DEFAULT nextval('public.transactions_id_seq'::regclass);


--
-- Name: videos video_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.videos ALTER COLUMN video_id SET DEFAULT nextval('public.videos_video_id_seq'::regclass);


--
-- Name: assets assets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_pkey PRIMARY KEY (asset_id);


--
-- Name: atomicmarket_template_buy_offer_listings atomicmarket_template_buy_offer_listings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.atomicmarket_template_buy_offer_listings
    ADD CONSTRAINT atomicmarket_template_buy_offer_listings_pkey PRIMARY KEY (buyoffer_id);


--
-- Name: atomicmarket_template_buy_offers atomicmarket_template_buy_offers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.atomicmarket_template_buy_offers
    ADD CONSTRAINT atomicmarket_template_buy_offers_pkey PRIMARY KEY (buyoffer_id);


--
-- Name: attributes attributes_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attributes
    ADD CONSTRAINT attributes_pk PRIMARY KEY (attribute_id);


--
-- Name: collections collections_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collections
    ADD CONSTRAINT collections_pkey PRIMARY KEY (collection);


--
-- Name: data data_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data
    ADD CONSTRAINT data_pkey PRIMARY KEY (data_id);


--
-- Name: images images_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_pkey PRIMARY KEY (image_id);


--
-- Name: memos memos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.memos
    ADD CONSTRAINT memos_pkey PRIMARY KEY (memo_id);


--
-- Name: mirror_swap_mints mirror_swap_mints_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mirror_swap_mints
    ADD CONSTRAINT mirror_swap_mints_pkey PRIMARY KEY (result_id);


--
-- Name: names names_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.names
    ADD CONSTRAINT names_pkey PRIMARY KEY (name_id);


--
-- Name: pfp_assets pfp_assets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pfp_assets
    ADD CONSTRAINT pfp_assets_pkey PRIMARY KEY (asset_id);


--
-- Name: rwax_assets rwax_assets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rwax_assets
    ADD CONSTRAINT rwax_assets_pkey PRIMARY KEY (asset_id);


--
-- Name: rwax_templates rwax_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rwax_templates
    ADD CONSTRAINT rwax_templates_pkey PRIMARY KEY (template_id);


--
-- Name: templates templates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.templates
    ADD CONSTRAINT templates_pkey PRIMARY KEY (template_id);


--
-- Name: transaction_ids transaction_ids_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transaction_ids
    ADD CONSTRAINT transaction_ids_pkey PRIMARY KEY (transaction_id);


--
-- Name: chronicle_transactions transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chronicle_transactions
    ADD CONSTRAINT transactions_pkey PRIMARY KEY (seq);


--
-- Name: videos videos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.videos
    ADD CONSTRAINT videos_pkey PRIMARY KEY (video_id);


--
-- Name: account_value_actions_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX account_value_actions_block_num_idx ON public.account_value_actions USING btree (block_num);


--
-- Name: account_value_actions_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX account_value_actions_seq_idx ON public.account_value_actions USING btree (seq DESC);


--
-- Name: asset_mints_asset_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX asset_mints_asset_id_idx ON public.asset_mints USING btree (asset_id DESC);


--
-- Name: asset_mints_asset_id_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX asset_mints_asset_id_idx1 ON public.asset_mints USING btree (asset_id);


--
-- Name: asset_mints_mint_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX asset_mints_mint_idx ON public.asset_mints USING btree (mint DESC);


--
-- Name: asset_mints_mint_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX asset_mints_mint_idx1 ON public.asset_mints USING btree (mint);


--
-- Name: asset_mints_template_id_mint_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX asset_mints_template_id_mint_idx ON public.asset_mints USING btree (template_id, mint DESC);


--
-- Name: asset_transfers_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX asset_transfers_block_num_idx ON public.transfers USING btree (block_num);


--
-- Name: asset_transfers_seq_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX asset_transfers_seq_idx1 ON public.transfers USING btree (seq DESC);


--
-- Name: assets_asset_id_attribute_ids_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX assets_asset_id_attribute_ids_idx ON public.assets USING btree (asset_id, attribute_ids);


--
-- Name: assets_asset_id_collection_schema_attribute_ids_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX assets_asset_id_collection_schema_attribute_ids_idx ON public.assets USING btree (asset_id, collection, schema, attribute_ids);


--
-- Name: assets_asset_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX assets_asset_id_idx ON public.assets USING btree (asset_id);


--
-- Name: assets_asset_id_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX assets_asset_id_idx1 ON public.assets USING btree (asset_id) WHERE (mint IS NULL);


--
-- Name: assets_asset_id_schema_attribute_ids_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX assets_asset_id_schema_attribute_ids_idx ON public.assets USING btree (asset_id, schema, attribute_ids);


--
-- Name: assets_attribute_ids_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX assets_attribute_ids_idx ON public.assets USING gin (attribute_ids);


--
-- Name: assets_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX assets_block_num_idx ON public.assets USING btree (block_num);


--
-- Name: assets_collection_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX assets_collection_idx ON public.assets USING btree (collection);


--
-- Name: assets_collection_name_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX assets_collection_name_id_idx ON public.assets USING btree (collection, name_id);


--
-- Name: assets_collection_schema_attribute_ids_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX assets_collection_schema_attribute_ids_idx ON public.assets USING btree (collection, schema, attribute_ids);


--
-- Name: assets_collection_schema_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX assets_collection_schema_idx ON public.assets USING btree (collection, schema);


--
-- Name: assets_collection_schema_name_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX assets_collection_schema_name_id_idx ON public.assets USING btree (collection, schema, name_id);


--
-- Name: assets_collection_schema_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX assets_collection_schema_seq_idx ON public.assets USING btree (collection, schema, seq DESC);


--
-- Name: assets_collection_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX assets_collection_seq_idx ON public.assets USING btree (collection, seq DESC);


--
-- Name: assets_image_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX assets_image_id_idx ON public.assets USING btree (image_id) WHERE (image_id = 16444);


--
-- Name: assets_mint_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX assets_mint_idx ON public.assets USING btree (mint);


--
-- Name: assets_name_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX assets_name_id_idx ON public.assets USING btree (name_id);


--
-- Name: assets_owner_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX assets_owner_idx ON public.assets USING btree (owner);


--
-- Name: assets_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX assets_seq_idx ON public.assets USING btree (seq DESC);


--
-- Name: assets_template_id_asset_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX assets_template_id_asset_id_idx ON public.assets USING btree (template_id, asset_id DESC);


--
-- Name: assets_template_id_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX assets_template_id_seq_idx ON public.assets USING btree (template_id, seq DESC);


--
-- Name: assets_timestamp_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX assets_timestamp_idx ON public.assets USING btree ("timestamp" DESC);


--
-- Name: assets_transferred_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX assets_transferred_idx ON public.assets USING btree (transferred DESC);


--
-- Name: assets_video_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX assets_video_id_idx ON public.assets USING btree (video_id) WHERE (video_id = 1);


--
-- Name: atomicassets_burns_asset_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicassets_burns_asset_id_idx ON public.atomicassets_burns USING btree (asset_id);


--
-- Name: atomicassets_burns_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicassets_burns_block_num_idx ON public.atomicassets_burns USING btree (block_num);


--
-- Name: atomicassets_burns_reversed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicassets_burns_reversed_block_num_idx ON public.atomicassets_burns_reversed USING btree (block_num);


--
-- Name: atomicassets_burns_reversed_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicassets_burns_reversed_seq_idx ON public.atomicassets_burns_reversed USING btree (seq DESC);


--
-- Name: atomicassets_burns_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicassets_burns_seq_idx ON public.atomicassets_burns USING btree (seq DESC);


--
-- Name: atomicassets_offer_logs_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicassets_offer_logs_block_num_idx ON public.atomicassets_offer_logs USING btree (block_num);


--
-- Name: atomicassets_offer_logs_offer_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicassets_offer_logs_offer_id_idx ON public.atomicassets_offer_logs USING btree (offer_id);


--
-- Name: atomicassets_offer_logs_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicassets_offer_logs_seq_idx ON public.atomicassets_offer_logs USING btree (seq DESC);


--
-- Name: atomicassets_offer_updates_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicassets_offer_updates_block_num_idx ON public.atomicassets_offer_updates USING btree (block_num);


--
-- Name: atomicassets_offer_updates_offer_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicassets_offer_updates_offer_id_idx ON public.atomicassets_offer_updates USING btree (offer_id);


--
-- Name: atomicassets_offer_updates_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicassets_offer_updates_seq_idx ON public.atomicassets_offer_updates USING btree (seq DESC);


--
-- Name: atomicassets_offers_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicassets_offers_block_num_idx ON public.atomicassets_offers USING btree (block_num);


--
-- Name: atomicassets_offers_offer_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicassets_offers_offer_id_idx ON public.atomicassets_offers USING btree (offer_id);


--
-- Name: atomicassets_offers_sender_asset_ids_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicassets_offers_sender_asset_ids_idx ON public.atomicassets_offers USING gin (sender_asset_ids);


--
-- Name: atomicassets_offers_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicassets_offers_seq_idx ON public.atomicassets_offers USING btree (seq DESC);


--
-- Name: atomicassets_updates_asset_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicassets_updates_asset_id_idx ON public.atomicassets_updates USING btree (asset_id);


--
-- Name: atomicassets_updates_asset_id_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicassets_updates_asset_id_idx1 ON public.atomicassets_updates USING btree (asset_id) WHERE (NOT applied);


--
-- Name: atomicassets_updates_asset_id_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicassets_updates_asset_id_seq_idx ON public.atomicassets_updates USING btree (asset_id, seq) WHERE (NOT applied);


--
-- Name: atomicassets_updates_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicassets_updates_block_num_idx ON public.atomicassets_updates USING btree (block_num);


--
-- Name: atomicassets_updates_reversed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicassets_updates_reversed_block_num_idx ON public.atomicassets_updates_reversed USING btree (block_num);


--
-- Name: atomicassets_updates_reversed_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicassets_updates_reversed_seq_idx ON public.atomicassets_updates_reversed USING btree (seq DESC);


--
-- Name: atomicassets_updates_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicassets_updates_seq_idx ON public.atomicassets_updates USING btree (seq DESC);


--
-- Name: atomicassets_updates_seq_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicassets_updates_seq_idx1 ON public.atomicassets_updates USING btree (seq) WHERE (NOT applied);


--
-- Name: atomicmarket_accept_buy_offers_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_accept_buy_offers_block_num_idx ON public.atomicmarket_accept_buy_offers USING btree (block_num);


--
-- Name: atomicmarket_accept_buy_offers_buyoffer_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_accept_buy_offers_buyoffer_id_idx ON public.atomicmarket_accept_buy_offers USING btree (buyoffer_id);


--
-- Name: atomicmarket_accept_buy_offers_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_accept_buy_offers_seq_idx ON public.atomicmarket_accept_buy_offers USING btree (seq DESC);


--
-- Name: atomicmarket_auction_cancels_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_auction_cancels_block_num_idx ON public.atomicmarket_auction_cancels USING btree (block_num);


--
-- Name: atomicmarket_auction_cancels_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_auction_cancels_seq_idx ON public.atomicmarket_auction_cancels USING btree (seq DESC);


--
-- Name: atomicmarket_buy_offers_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_buy_offers_block_num_idx ON public.atomicmarket_buy_offers USING btree (block_num);


--
-- Name: atomicmarket_buy_offers_buyoffer_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_buy_offers_buyoffer_id_idx ON public.atomicmarket_buy_offers USING btree (buyoffer_id);


--
-- Name: atomicmarket_buy_offers_buyoffer_id_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX atomicmarket_buy_offers_buyoffer_id_idx1 ON public.atomicmarket_buy_offers USING btree (buyoffer_id);


--
-- Name: atomicmarket_buy_offers_listings_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_buy_offers_listings_block_num_idx ON public.atomicmarket_buy_offers_listings USING btree (block_num);


--
-- Name: atomicmarket_buy_offers_listings_buyoffer_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_buy_offers_listings_buyoffer_id_idx ON public.atomicmarket_buy_offers_listings USING btree (buyoffer_id);


--
-- Name: atomicmarket_buy_offers_listings_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_buy_offers_listings_seq_idx ON public.atomicmarket_buy_offers_listings USING btree (seq DESC);


--
-- Name: atomicmarket_buy_offers_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_buy_offers_seq_idx ON public.atomicmarket_buy_offers USING btree (seq DESC);


--
-- Name: atomicmarket_cancel_buy_offers_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_cancel_buy_offers_block_num_idx ON public.atomicmarket_cancel_buy_offers USING btree (block_num);


--
-- Name: atomicmarket_cancel_buy_offers_buyoffer_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_cancel_buy_offers_buyoffer_id_idx ON public.atomicmarket_cancel_buy_offers USING btree (buyoffer_id);


--
-- Name: atomicmarket_cancel_buy_offers_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_cancel_buy_offers_seq_idx ON public.atomicmarket_cancel_buy_offers USING btree (seq DESC);


--
-- Name: atomicmarket_cancel_template_buy_offers_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_cancel_template_buy_offers_block_num_idx ON public.atomicmarket_cancel_template_buy_offers USING btree (block_num);


--
-- Name: atomicmarket_cancel_template_buy_offers_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_cancel_template_buy_offers_seq_idx ON public.atomicmarket_cancel_template_buy_offers USING btree (seq DESC);


--
-- Name: atomicmarket_cancels_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_cancels_block_num_idx ON public.atomicmarket_cancels USING btree (block_num);


--
-- Name: atomicmarket_cancels_listing_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_cancels_listing_id_idx ON public.atomicmarket_cancels USING btree (listing_id);


--
-- Name: atomicmarket_cancels_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_cancels_seq_idx ON public.atomicmarket_cancels USING btree (seq DESC);


--
-- Name: atomicmarket_cancels_timestamp_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_cancels_timestamp_idx ON public.atomicmarket_cancels USING btree ("timestamp");


--
-- Name: atomicmarket_decline_buy_offers_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_decline_buy_offers_block_num_idx ON public.atomicmarket_decline_buy_offers USING btree (block_num);


--
-- Name: atomicmarket_decline_buy_offers_buyoffer_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_decline_buy_offers_buyoffer_id_idx ON public.atomicmarket_decline_buy_offers USING btree (buyoffer_id);


--
-- Name: atomicmarket_decline_buy_offers_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_decline_buy_offers_seq_idx ON public.atomicmarket_decline_buy_offers USING btree (seq DESC);


--
-- Name: atomicmarket_fulfill_template_buy_offers_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_fulfill_template_buy_offers_block_num_idx ON public.atomicmarket_fulfill_template_buy_offers USING btree (block_num);


--
-- Name: atomicmarket_fulfill_template_buy_offers_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_fulfill_template_buy_offers_seq_idx ON public.atomicmarket_fulfill_template_buy_offers USING btree (seq DESC);


--
-- Name: atomicmarket_listings_asset_ids_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_listings_asset_ids_idx ON public.atomicmarket_listings USING gin (asset_ids);


--
-- Name: atomicmarket_listings_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_listings_block_num_idx ON public.atomicmarket_listings USING btree (block_num);


--
-- Name: atomicmarket_listings_listing_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_listings_listing_id_idx ON public.atomicmarket_listings USING btree (listing_id);


--
-- Name: atomicmarket_listings_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_listings_seq_idx ON public.atomicmarket_listings USING btree (seq DESC);


--
-- Name: atomicmarket_purchases_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_purchases_block_num_idx ON public.atomicmarket_purchases USING btree (block_num);


--
-- Name: atomicmarket_purchases_listing_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_purchases_listing_id_idx ON public.atomicmarket_purchases USING btree (listing_id);


--
-- Name: atomicmarket_purchases_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_purchases_seq_idx ON public.atomicmarket_purchases USING btree (seq DESC);


--
-- Name: atomicmarket_purchases_timestamp_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_purchases_timestamp_idx ON public.atomicmarket_purchases USING btree ("timestamp" DESC);


--
-- Name: atomicmarket_purchases_timestamp_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_purchases_timestamp_idx1 ON public.atomicmarket_purchases USING btree ("timestamp");


--
-- Name: atomicmarket_sale_starts_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_sale_starts_block_num_idx ON public.atomicmarket_sale_starts USING btree (block_num);


--
-- Name: atomicmarket_sale_starts_listing_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_sale_starts_listing_id_idx ON public.atomicmarket_sale_starts USING btree (listing_id);


--
-- Name: atomicmarket_sale_starts_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_sale_starts_seq_idx ON public.atomicmarket_sale_starts USING btree (seq DESC);


--
-- Name: atomicmarket_template_buy_offer_listings_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_template_buy_offer_listings_block_num_idx ON public.atomicmarket_template_buy_offer_listings USING btree (block_num);


--
-- Name: atomicmarket_template_buy_offer_listings_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_template_buy_offer_listings_seq_idx ON public.atomicmarket_template_buy_offer_listings USING btree (seq DESC);


--
-- Name: atomicmarket_template_buy_offers_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_template_buy_offers_block_num_idx ON public.atomicmarket_template_buy_offers USING btree (block_num);


--
-- Name: atomicmarket_template_buy_offers_buyer_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_template_buy_offers_buyer_idx ON public.atomicmarket_template_buy_offers USING btree (buyer);


--
-- Name: atomicmarket_template_buy_offers_collection_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_template_buy_offers_collection_idx ON public.atomicmarket_template_buy_offers USING btree (collection);


--
-- Name: atomicmarket_template_buy_offers_price_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_template_buy_offers_price_idx ON public.atomicmarket_template_buy_offers USING btree (price DESC);


--
-- Name: atomicmarket_template_buy_offers_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_template_buy_offers_seq_idx ON public.atomicmarket_template_buy_offers USING btree (seq DESC);


--
-- Name: atomicmarket_template_buy_offers_template_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_template_buy_offers_template_id_idx ON public.atomicmarket_template_buy_offers USING btree (template_id);


--
-- Name: atomicmarket_template_buy_offers_template_id_price_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_template_buy_offers_template_id_price_idx ON public.atomicmarket_template_buy_offers USING btree (template_id, price DESC);


--
-- Name: atomicmarket_template_buy_offers_timestamp_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX atomicmarket_template_buy_offers_timestamp_idx ON public.atomicmarket_template_buy_offers USING btree ("timestamp" DESC);


--
-- Name: attribute_floors_mv_attribute_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX attribute_floors_mv_attribute_id_idx ON public.attribute_floors_mv USING btree (attribute_id);


--
-- Name: attribute_stats_attribute_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX attribute_stats_attribute_id_idx ON public.attribute_stats USING btree (attribute_id);


--
-- Name: attributes_author_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX attributes_author_idx ON public.attributes USING btree (collection);


--
-- Name: attributes_author_schema_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX attributes_author_schema_idx ON public.attributes USING btree (collection, schema);


--
-- Name: attributes_collection_schema_attribute_name_float_value_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX attributes_collection_schema_attribute_name_float_value_idx ON public.attributes USING btree (collection, schema, attribute_name, float_value) WHERE (float_value IS NOT NULL);


--
-- Name: attributes_collection_schema_attribute_name_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX attributes_collection_schema_attribute_name_idx ON public.attributes USING btree (collection, schema, attribute_name);


--
-- Name: attributes_collection_schema_attribute_name_int_value_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX attributes_collection_schema_attribute_name_int_value_idx ON public.attributes USING btree (collection, schema, attribute_name, int_value) WHERE (int_value IS NOT NULL);


--
-- Name: auction_bids_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auction_bids_block_num_idx ON public.auction_bids USING btree (block_num);


--
-- Name: auction_bids_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auction_bids_seq_idx ON public.auction_bids USING btree (seq DESC);


--
-- Name: auction_claims_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auction_claims_block_num_idx ON public.auction_claims USING btree (block_num);


--
-- Name: auction_claims_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auction_claims_seq_idx ON public.auction_claims USING btree (seq DESC);


--
-- Name: auction_logs_auction_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auction_logs_auction_id_idx ON public.auction_logs USING btree (auction_id);


--
-- Name: auction_logs_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auction_logs_block_num_idx ON public.auction_logs USING btree (block_num);


--
-- Name: auction_logs_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auction_logs_seq_idx ON public.auction_logs USING btree (seq DESC);


--
-- Name: auctions_auction_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auctions_auction_id_idx ON public.auctions USING btree (auction_id);


--
-- Name: auctions_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auctions_block_num_idx ON public.auctions USING btree (block_num);


--
-- Name: auctions_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auctions_seq_idx ON public.auctions USING btree (seq DESC);


--
-- Name: backed_assets_asset_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX backed_assets_asset_id_idx ON public.backed_assets USING btree (asset_id);


--
-- Name: backed_assets_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX backed_assets_block_num_idx ON public.backed_assets USING btree (block_num);


--
-- Name: backed_assets_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX backed_assets_seq_idx ON public.backed_assets USING btree (seq DESC);


--
-- Name: badges_collection_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX badges_collection_idx ON public.badges USING btree (collection);


--
-- Name: banners_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX banners_block_num_idx ON public.banners USING btree (block_num);


--
-- Name: banners_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX banners_seq_idx ON public.banners USING btree (seq DESC);


--
-- Name: buyer_volumes_mv_user_name_collection_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX buyer_volumes_mv_user_name_collection_type_idx ON public.buyer_volumes_mv USING btree (user_name, collection, type);


--
-- Name: buyoffer_balance_updates_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX buyoffer_balance_updates_block_num_idx ON public.buyoffer_balance_updates USING btree (block_num);


--
-- Name: buyoffer_balance_updates_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX buyoffer_balance_updates_seq_idx ON public.buyoffer_balance_updates USING btree (seq DESC);


--
-- Name: buyoffer_cancels_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX buyoffer_cancels_block_num_idx ON public.buyoffer_cancels USING btree (block_num);


--
-- Name: buyoffer_cancels_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX buyoffer_cancels_seq_idx ON public.buyoffer_cancels USING btree (seq DESC);


--
-- Name: buyoffer_purchases_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX buyoffer_purchases_block_num_idx ON public.buyoffer_purchases USING btree (block_num);


--
-- Name: buyoffer_purchases_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX buyoffer_purchases_seq_idx ON public.buyoffer_purchases USING btree (seq DESC);


--
-- Name: buyoffers_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX buyoffers_block_num_idx ON public.buyoffers USING btree (block_num);


--
-- Name: buyoffers_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX buyoffers_seq_idx ON public.buyoffers USING btree (seq DESC);


--
-- Name: canceled_atomic_listings_sale_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX canceled_atomic_listings_sale_id_idx ON public.removed_atomic_listings USING btree (sale_id);


--
-- Name: canceled_atomic_listings_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX canceled_atomic_listings_seq_idx ON public.removed_atomic_listings USING btree (seq DESC);


--
-- Name: chronicle_transactions_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX chronicle_transactions_block_num_idx ON public.chronicle_transactions USING btree (block_num DESC);


--
-- Name: chronicle_transactions_seq_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX chronicle_transactions_seq_idx1 ON public.chronicle_transactions USING btree (seq) WHERE (NOT ingested);


--
-- Name: collection_account_updates_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX collection_account_updates_block_num_idx ON public.collection_account_updates USING btree (block_num);


--
-- Name: collection_account_updates_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX collection_account_updates_seq_idx ON public.collection_account_updates USING btree (seq DESC);


--
-- Name: collection_assets_mv_collection_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX collection_assets_mv_collection_idx ON public.collection_assets_mv USING btree (collection);


--
-- Name: collection_badges_mv_collection_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX collection_badges_mv_collection_idx ON public.collection_badges_mv USING btree (collection);


--
-- Name: collection_fee_updates_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX collection_fee_updates_block_num_idx ON public.collection_fee_updates USING btree (block_num);


--
-- Name: collection_fee_updates_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX collection_fee_updates_seq_idx ON public.collection_fee_updates USING btree (seq DESC);


--
-- Name: collection_market_cap_mv_collection_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX collection_market_cap_mv_collection_idx ON public.collection_market_cap_mv USING btree (collection);


--
-- Name: collection_sales_by_date_before_2024_mv_to_date_collection_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX collection_sales_by_date_before_2024_mv_to_date_collection_idx ON public.collection_sales_by_date_before_2024_mv USING btree (to_date DESC, collection);


--
-- Name: collection_sales_by_date_before_202_collection_type_to_date_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX collection_sales_by_date_before_202_collection_type_to_date_idx ON public.collection_sales_by_date_before_2024_mv USING btree (collection, type, to_date);


--
-- Name: collection_sales_by_date_from_2024__collection_type_to_date_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX collection_sales_by_date_from_2024__collection_type_to_date_idx ON public.collection_sales_by_date_from_2024_mv USING btree (collection, type, to_date);


--
-- Name: collection_sales_by_date_from_2024_mv_to_date_collection_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX collection_sales_by_date_from_2024_mv_to_date_collection_idx ON public.collection_sales_by_date_from_2024_mv USING btree (to_date DESC, collection);


--
-- Name: collection_sales_by_date_mv_collection_type_to_date_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX collection_sales_by_date_mv_collection_type_to_date_idx ON public.collection_sales_by_date_mv USING btree (collection, type, to_date);


--
-- Name: collection_sales_by_date_mv_to_date_collection_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX collection_sales_by_date_mv_to_date_collection_idx ON public.collection_sales_by_date_mv USING btree (to_date DESC, collection);


--
-- Name: collection_tag_ids_mv_collection_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX collection_tag_ids_mv_collection_idx ON public.collection_tag_ids_mv USING btree (collection);


--
-- Name: collection_tag_ids_mv_tag_ids_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX collection_tag_ids_mv_tag_ids_idx ON public.collection_tag_ids_mv USING gin (tag_ids);


--
-- Name: collection_updates_block_num_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX collection_updates_block_num_idx1 ON public.collection_updates USING btree (block_num);


--
-- Name: collection_updates_collection_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX collection_updates_collection_idx ON public.collection_updates USING btree (collection);


--
-- Name: collection_updates_seq_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX collection_updates_seq_idx1 ON public.collection_updates USING btree (seq DESC);


--
-- Name: collection_user_count_mv_collection_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX collection_user_count_mv_collection_idx ON public.collection_user_count_mv USING btree (collection);


--
-- Name: collection_users_mv_owner_collection_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX collection_users_mv_owner_collection_idx ON public.collection_users_mv USING btree (owner, collection);


--
-- Name: collection_volumes_14_mv_collection_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX collection_volumes_14_mv_collection_type_idx ON public.collection_volumes_14_mv USING btree (collection, type);


--
-- Name: collection_volumes_15_mv_collection_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX collection_volumes_15_mv_collection_type_idx ON public.collection_volumes_15_mv USING btree (collection, type);


--
-- Name: collection_volumes_180_mv_collection_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX collection_volumes_180_mv_collection_type_idx ON public.collection_volumes_180_mv USING btree (collection, type);


--
-- Name: collection_volumes_1_mv_collection_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX collection_volumes_1_mv_collection_type_idx ON public.collection_volumes_1_mv USING btree (collection, type);


--
-- Name: collection_volumes_2_mv_collection_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX collection_volumes_2_mv_collection_type_idx ON public.collection_volumes_2_mv USING btree (collection, type);


--
-- Name: collection_volumes_30_mv_collection_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX collection_volumes_30_mv_collection_type_idx ON public.collection_volumes_30_mv USING btree (collection, type);


--
-- Name: collection_volumes_365_mv_collection_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX collection_volumes_365_mv_collection_type_idx ON public.collection_volumes_365_mv USING btree (collection, type);


--
-- Name: collection_volumes_3_mv_collection_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX collection_volumes_3_mv_collection_type_idx ON public.collection_volumes_3_mv USING btree (collection, type);


--
-- Name: collection_volumes_60_mv_collection_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX collection_volumes_60_mv_collection_type_idx ON public.collection_volumes_60_mv USING btree (collection, type);


--
-- Name: collection_volumes_7_mv_collection_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX collection_volumes_7_mv_collection_type_idx ON public.collection_volumes_7_mv USING btree (collection, type);


--
-- Name: collection_volumes_90_mv_collection_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX collection_volumes_90_mv_collection_type_idx ON public.collection_volumes_90_mv USING btree (collection, type);


--
-- Name: collection_volumes_from_2023_mv_collection_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX collection_volumes_from_2023_mv_collection_type_idx ON public.collection_volumes_from_2023_mv USING btree (collection, type);


--
-- Name: collection_volumes_s_mv_type_collection_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX collection_volumes_s_mv_type_collection_idx ON public.collection_volumes_s_mv USING btree (type, collection);


--
-- Name: collection_votes_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX collection_votes_block_num_idx ON public.collection_votes USING btree (block_num);


--
-- Name: collection_votes_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX collection_votes_seq_idx ON public.collection_votes USING btree (seq DESC);


--
-- Name: collections_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX collections_block_num_idx ON public.collections USING btree (block_num);


--
-- Name: collections_collection_verified_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX collections_collection_verified_idx ON public.collections USING btree (collection, verified);


--
-- Name: collections_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX collections_seq_idx ON public.collections USING btree (seq DESC);


--
-- Name: craft_action_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX craft_action_block_num_idx ON public.craft_actions USING btree (block_num);


--
-- Name: craft_action_craft_id_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX craft_action_craft_id_seq_idx ON public.craft_actions USING btree (craft_id, seq DESC);


--
-- Name: craft_action_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX craft_action_seq_idx ON public.craft_actions USING btree (seq DESC);


--
-- Name: craft_erase_updates_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX craft_erase_updates_block_num_idx ON public.craft_erase_updates USING btree (block_num DESC);


--
-- Name: craft_erase_updates_block_num_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX craft_erase_updates_block_num_idx1 ON public.craft_erase_updates USING btree (block_num);


--
-- Name: craft_erase_updates_reversed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX craft_erase_updates_reversed_block_num_idx ON public.craft_erase_updates_reversed USING btree (block_num);


--
-- Name: craft_erase_updates_reversed_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX craft_erase_updates_reversed_seq_idx ON public.craft_erase_updates_reversed USING btree (seq DESC);


--
-- Name: craft_erase_updates_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX craft_erase_updates_seq_idx ON public.craft_erase_updates USING btree (seq DESC);


--
-- Name: craft_erase_updates_seq_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX craft_erase_updates_seq_idx1 ON public.craft_erase_updates USING btree (seq DESC);


--
-- Name: craft_minting_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX craft_minting_block_num_idx ON public.craft_minting USING btree (block_num);


--
-- Name: craft_minting_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX craft_minting_seq_idx ON public.craft_minting USING btree (seq DESC);


--
-- Name: craft_ready_updates_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX craft_ready_updates_block_num_idx ON public.craft_ready_updates USING btree (block_num);


--
-- Name: craft_ready_updates_reversed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX craft_ready_updates_reversed_block_num_idx ON public.craft_ready_updates_reversed USING btree (block_num);


--
-- Name: craft_ready_updates_reversed_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX craft_ready_updates_reversed_seq_idx ON public.craft_ready_updates_reversed USING btree (seq DESC);


--
-- Name: craft_ready_updates_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX craft_ready_updates_seq_idx ON public.craft_ready_updates USING btree (seq DESC);


--
-- Name: craft_results_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX craft_results_block_num_idx ON public.craft_results USING btree (block_num);


--
-- Name: craft_results_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX craft_results_seq_idx ON public.craft_results USING btree (seq DESC);


--
-- Name: craft_total_updates_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX craft_total_updates_block_num_idx ON public.craft_total_updates USING btree (block_num);


--
-- Name: craft_total_updates_reversed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX craft_total_updates_reversed_block_num_idx ON public.craft_total_updates_reversed USING btree (block_num);


--
-- Name: craft_total_updates_reversed_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX craft_total_updates_reversed_seq_idx ON public.craft_total_updates_reversed USING btree (seq DESC);


--
-- Name: craft_total_updates_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX craft_total_updates_seq_idx ON public.craft_total_updates USING btree (seq DESC);


--
-- Name: craft_updates_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX craft_updates_block_num_idx ON public.craft_updates USING btree (block_num);


--
-- Name: craft_updates_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX craft_updates_seq_idx ON public.craft_updates USING btree (seq DESC);


--
-- Name: data_md5_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX data_md5_idx ON public.data USING btree (md5(data));


--
-- Name: drop_actions_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_actions_seq_idx ON public.drop_actions USING btree (seq DESC);


--
-- Name: drop_auth_updates_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_auth_updates_block_num_idx ON public.drop_auth_updates USING btree (block_num);


--
-- Name: drop_auth_updates_reversed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_auth_updates_reversed_block_num_idx ON public.drop_auth_updates_reversed USING btree (block_num);


--
-- Name: drop_auth_updates_reversed_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_auth_updates_reversed_seq_idx ON public.drop_auth_updates_reversed USING btree (seq DESC);


--
-- Name: drop_auth_updates_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_auth_updates_seq_idx ON public.drop_auth_updates USING btree (seq DESC);


--
-- Name: drop_claim_counts_mv_contract_drop_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX drop_claim_counts_mv_contract_drop_id_idx ON public.drop_claim_counts_mv USING btree (contract, drop_id);


--
-- Name: drop_claims_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_claims_block_num_idx ON public.drop_claims USING btree (block_num);


--
-- Name: drop_claims_contract_drop_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_claims_contract_drop_id_idx ON public.drop_claims USING btree (contract, drop_id);


--
-- Name: drop_claims_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_claims_seq_idx ON public.drop_claims USING btree (seq DESC);


--
-- Name: drop_display_updates_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_display_updates_block_num_idx ON public.drop_display_updates USING btree (block_num);


--
-- Name: drop_display_updates_reversed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_display_updates_reversed_block_num_idx ON public.drop_display_updates_reversed USING btree (block_num);


--
-- Name: drop_display_updates_reversed_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_display_updates_reversed_seq_idx ON public.drop_display_updates_reversed USING btree (seq DESC);


--
-- Name: drop_display_updates_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_display_updates_seq_idx ON public.drop_display_updates USING btree (seq DESC);


--
-- Name: drop_erase_updates_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_erase_updates_block_num_idx ON public.drop_erase_updates USING btree (block_num);


--
-- Name: drop_erase_updates_reversed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_erase_updates_reversed_block_num_idx ON public.drop_erase_updates_reversed USING btree (block_num);


--
-- Name: drop_erase_updates_reversed_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_erase_updates_reversed_seq_idx ON public.drop_erase_updates_reversed USING btree (seq DESC);


--
-- Name: drop_erase_updates_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_erase_updates_seq_idx ON public.drop_erase_updates USING btree (seq DESC);


--
-- Name: drop_fee_updates_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_fee_updates_block_num_idx ON public.drop_fee_updates USING btree (block_num);


--
-- Name: drop_fee_updates_reversed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_fee_updates_reversed_block_num_idx ON public.drop_fee_updates_reversed USING btree (block_num);


--
-- Name: drop_fee_updates_reversed_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_fee_updates_reversed_seq_idx ON public.drop_fee_updates_reversed USING btree (seq DESC);


--
-- Name: drop_fee_updates_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_fee_updates_seq_idx ON public.drop_fee_updates USING btree (seq DESC);


--
-- Name: drop_hidden_updates_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_hidden_updates_block_num_idx ON public.drop_hidden_updates USING btree (block_num);


--
-- Name: drop_hidden_updates_reversed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_hidden_updates_reversed_block_num_idx ON public.drop_hidden_updates_reversed USING btree (block_num);


--
-- Name: drop_hidden_updates_reversed_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_hidden_updates_reversed_seq_idx ON public.drop_hidden_updates_reversed USING btree (seq DESC);


--
-- Name: drop_hidden_updates_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_hidden_updates_seq_idx ON public.drop_hidden_updates USING btree (seq DESC);


--
-- Name: drop_limit_updates_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_limit_updates_block_num_idx ON public.drop_limit_updates USING btree (block_num);


--
-- Name: drop_limit_updates_reversed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_limit_updates_reversed_block_num_idx ON public.drop_limit_updates_reversed USING btree (block_num);


--
-- Name: drop_limit_updates_reversed_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_limit_updates_reversed_seq_idx ON public.drop_limit_updates_reversed USING btree (seq DESC);


--
-- Name: drop_limit_updates_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_limit_updates_seq_idx ON public.drop_limit_updates USING btree (seq DESC);


--
-- Name: drop_log_prices_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_log_prices_block_num_idx ON public.drop_log_prices USING btree (block_num);


--
-- Name: drop_log_prices_drop_id_contract_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_log_prices_drop_id_contract_seq_idx ON public.drop_log_prices USING btree (drop_id, contract, seq DESC);


--
-- Name: drop_log_prices_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_log_prices_seq_idx ON public.drop_log_prices USING btree (seq DESC);


--
-- Name: drop_max_updates_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_max_updates_block_num_idx ON public.drop_max_updates USING btree (block_num);


--
-- Name: drop_max_updates_reversed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_max_updates_reversed_block_num_idx ON public.drop_max_updates_reversed USING btree (block_num);


--
-- Name: drop_max_updates_reversed_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_max_updates_reversed_seq_idx ON public.drop_max_updates_reversed USING btree (seq DESC);


--
-- Name: drop_max_updates_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_max_updates_seq_idx ON public.drop_max_updates USING btree (seq DESC);


--
-- Name: drop_price_updates_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_price_updates_block_num_idx ON public.drop_price_updates USING btree (block_num);


--
-- Name: drop_price_updates_contract_drop_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_price_updates_contract_drop_id_idx ON public.drop_price_updates USING btree (contract, drop_id DESC);


--
-- Name: drop_price_updates_reversed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_price_updates_reversed_block_num_idx ON public.drop_price_updates_reversed USING btree (block_num);


--
-- Name: drop_price_updates_reversed_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_price_updates_reversed_seq_idx ON public.drop_price_updates_reversed USING btree (seq DESC);


--
-- Name: drop_price_updates_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_price_updates_seq_idx ON public.drop_price_updates USING btree (seq DESC);


--
-- Name: drop_prices_mv_drop_id_contract_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX drop_prices_mv_drop_id_contract_idx ON public.drop_prices_mv USING btree (drop_id, contract);


--
-- Name: drop_times_updates_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_times_updates_block_num_idx ON public.drop_times_updates USING btree (block_num);


--
-- Name: drop_times_updates_reversed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_times_updates_reversed_block_num_idx ON public.drop_times_updates_reversed USING btree (block_num);


--
-- Name: drop_times_updates_reversed_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_times_updates_reversed_seq_idx ON public.drop_times_updates_reversed USING btree (seq DESC);


--
-- Name: drop_times_updates_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drop_times_updates_seq_idx ON public.drop_times_updates USING btree (seq DESC);


--
-- Name: drops_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drops_block_num_idx ON public.drops USING btree (block_num);


--
-- Name: drops_contract_drop_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX drops_contract_drop_id_idx ON public.drops USING btree (contract, drop_id);


--
-- Name: drops_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drops_seq_idx ON public.drops USING btree (seq DESC);


--
-- Name: drops_templates_to_mint_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX drops_templates_to_mint_idx ON public.drops USING gin (templates_to_mint);


--
-- Name: error_transactions_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX error_transactions_block_num_idx ON public.error_transactions USING btree (block_num);


--
-- Name: error_transactions_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX error_transactions_seq_idx ON public.error_transactions USING btree (seq DESC);


--
-- Name: favorites_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX favorites_block_num_idx ON public.favorites USING btree (block_num);


--
-- Name: favorites_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX favorites_seq_idx ON public.favorites USING btree (seq DESC);


--
-- Name: favorites_user_name_asset_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX favorites_user_name_asset_id_idx ON public.favorites USING btree (user_name, asset_id);


--
-- Name: favorites_user_name_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX favorites_user_name_idx ON public.favorites USING btree (user_name);


--
-- Name: favorites_user_name_template_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX favorites_user_name_template_id_idx ON public.favorites USING btree (user_name, template_id);


--
-- Name: floor_prices_by_date_template_id_floor_date_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX floor_prices_by_date_template_id_floor_date_idx ON public.floor_prices_by_date USING btree (template_id, floor_date DESC);


--
-- Name: floor_prices_mv_floor_price_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX floor_prices_mv_floor_price_idx ON public.floor_prices_mv USING btree (floor_price);


--
-- Name: floor_prices_mv_floor_price_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX floor_prices_mv_floor_price_idx1 ON public.floor_prices_mv USING btree (floor_price DESC);


--
-- Name: floor_prices_mv_template_id_floor_price_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX floor_prices_mv_template_id_floor_price_idx ON public.floor_prices_mv USING btree (template_id, floor_price DESC);


--
-- Name: floor_prices_mv_template_id_floor_price_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX floor_prices_mv_template_id_floor_price_idx1 ON public.floor_prices_mv USING btree (template_id, floor_price);


--
-- Name: floor_prices_mv_template_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX floor_prices_mv_template_id_idx ON public.floor_prices_mv USING btree (template_id);


--
-- Name: floor_template_mv_collection_template_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX floor_template_mv_collection_template_id_idx ON public.floor_template_mv USING btree (collection, template_id);


--
-- Name: follows_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX follows_block_num_idx ON public.follows USING btree (block_num);


--
-- Name: follows_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX follows_seq_idx ON public.follows USING btree (seq DESC);


--
-- Name: forks_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX forks_block_num_idx ON public.forks USING btree (block_num);


--
-- Name: ft_listings_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ft_listings_block_num_idx ON public.ft_listings USING btree (block_num);


--
-- Name: ft_listings_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ft_listings_seq_idx ON public.ft_listings USING btree (seq DESC);


--
-- Name: handle_fork_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX handle_fork_block_num_idx ON public.handle_fork USING btree (block_num);


--
-- Name: images_image_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX images_image_idx ON public.images USING btree (image);


--
-- Name: listings_asset_ids_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX listings_asset_ids_idx ON public.listings USING gin (asset_ids);


--
-- Name: listings_asset_ids_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX listings_asset_ids_idx1 ON public.listings USING btree ((asset_ids[1]));


--
-- Name: listings_asset_ids_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX listings_asset_ids_idx2 ON public.listings USING btree ((asset_ids[1])) WHERE (array_length(asset_ids, 1) = 1);


--
-- Name: listings_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX listings_block_num_idx ON public.listings USING btree (block_num);


--
-- Name: listings_collection_estimated_wax_price_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX listings_collection_estimated_wax_price_idx ON public.listings USING btree (collection, estimated_wax_price);


--
-- Name: listings_collection_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX listings_collection_idx ON public.listings USING btree (collection);


--
-- Name: listings_collection_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX listings_collection_idx1 ON public.listings USING btree (collection) WHERE (array_length(asset_ids, 1) = 1);


--
-- Name: listings_currency_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX listings_currency_idx ON public.listings USING btree (currency) WHERE ((currency)::text = 'USD'::text);


--
-- Name: listings_currency_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX listings_currency_idx1 ON public.listings USING btree (currency DESC);


--
-- Name: listings_estimated_wax_price_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX listings_estimated_wax_price_idx ON public.listings USING btree (estimated_wax_price);


--
-- Name: listings_floor_breakdown_mv_collection_schema_template_id_a_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX listings_floor_breakdown_mv_collection_schema_template_id_a_idx ON public.listings_floor_breakdown_mv USING btree (collection, schema, template_id, attribute_id);


--
-- Name: listings_helper_mv_mint_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX listings_helper_mv_mint_idx ON public.listings_helper_mv USING btree (mint DESC);


--
-- Name: listings_helper_mv_name_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX listings_helper_mv_name_idx ON public.listings_helper_mv USING btree (name);


--
-- Name: listings_helper_mv_sale_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX listings_helper_mv_sale_id_idx ON public.listings_helper_mv USING btree (sale_id);


--
-- Name: listings_helper_mv_template_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX listings_helper_mv_template_id_idx ON public.listings_helper_mv USING btree (template_id);


--
-- Name: listings_market_asset_ids_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX listings_market_asset_ids_idx ON public.listings USING btree (market, asset_ids);


--
-- Name: listings_market_listing_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX listings_market_listing_id_idx ON public.listings USING btree (market, listing_id);


--
-- Name: listings_market_seller_asset_ids_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX listings_market_seller_asset_ids_idx ON public.listings USING btree (market, seller, asset_ids);


--
-- Name: listings_price_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX listings_price_idx ON public.listings USING btree (price) WHERE ((currency)::text = 'USD'::text);


--
-- Name: listings_sale_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX listings_sale_id_idx ON public.listings USING btree (sale_id);


--
-- Name: listings_sale_id_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX listings_sale_id_idx1 ON public.listings USING btree (sale_id) WHERE (array_length(asset_ids, 1) = 1);


--
-- Name: listings_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX listings_seq_idx ON public.listings USING btree (seq DESC);


--
-- Name: listings_timestamp_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX listings_timestamp_idx ON public.listings USING btree ("timestamp" DESC);


--
-- Name: market_actions_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX market_actions_block_num_idx ON public.market_actions USING btree (block_num);


--
-- Name: market_actions_market_sale_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX market_actions_market_sale_id_idx ON public.market_actions USING btree (market, sale_id);


--
-- Name: market_actions_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX market_actions_seq_idx ON public.market_actions USING btree (seq DESC);


--
-- Name: market_collection_volumes_14__collection_market_taker_maker_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX market_collection_volumes_14__collection_market_taker_maker_idx ON public.market_collection_volumes_14_mv USING btree (collection, market, taker, maker, type);


--
-- Name: market_collection_volumes_15__collection_market_taker_maker_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX market_collection_volumes_15__collection_market_taker_maker_idx ON public.market_collection_volumes_15_mv USING btree (collection, market, taker, maker, type);


--
-- Name: market_collection_volumes_180_collection_market_taker_maker_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX market_collection_volumes_180_collection_market_taker_maker_idx ON public.market_collection_volumes_180_mv USING btree (collection, market, taker, maker, type);


--
-- Name: market_collection_volumes_1_m_collection_market_taker_maker_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX market_collection_volumes_1_m_collection_market_taker_maker_idx ON public.market_collection_volumes_1_mv USING btree (collection, market, taker, maker, type);


--
-- Name: market_collection_volumes_2_m_collection_market_taker_maker_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX market_collection_volumes_2_m_collection_market_taker_maker_idx ON public.market_collection_volumes_2_mv USING btree (collection, market, taker, maker, type);


--
-- Name: market_collection_volumes_30__collection_market_taker_maker_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX market_collection_volumes_30__collection_market_taker_maker_idx ON public.market_collection_volumes_30_mv USING btree (collection, market, taker, maker, type);


--
-- Name: market_collection_volumes_365_collection_market_taker_maker_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX market_collection_volumes_365_collection_market_taker_maker_idx ON public.market_collection_volumes_365_mv USING btree (collection, market, taker, maker, type);


--
-- Name: market_collection_volumes_3_m_collection_market_taker_maker_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX market_collection_volumes_3_m_collection_market_taker_maker_idx ON public.market_collection_volumes_3_mv USING btree (collection, market, taker, maker, type);


--
-- Name: market_collection_volumes_60__collection_market_taker_maker_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX market_collection_volumes_60__collection_market_taker_maker_idx ON public.market_collection_volumes_60_mv USING btree (collection, market, taker, maker, type);


--
-- Name: market_collection_volumes_7_m_collection_market_taker_maker_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX market_collection_volumes_7_m_collection_market_taker_maker_idx ON public.market_collection_volumes_7_mv USING btree (collection, market, taker, maker, type);


--
-- Name: market_collection_volumes_90__collection_market_taker_maker_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX market_collection_volumes_90__collection_market_taker_maker_idx ON public.market_collection_volumes_90_mv USING btree (collection, market, taker, maker, type);


--
-- Name: market_collection_volumes_fro_collection_market_taker_maker_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX market_collection_volumes_fro_collection_market_taker_maker_idx ON public.market_collection_volumes_from_2023_mv USING btree (collection, market, taker, maker, type);


--
-- Name: market_statuses_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX market_statuses_block_num_idx ON public.market_statuses USING btree (block_num);


--
-- Name: market_statuses_market_list_name_collection_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX market_statuses_market_list_name_collection_idx ON public.market_statuses USING btree (market, list_name, collection);


--
-- Name: market_statuses_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX market_statuses_seq_idx ON public.market_statuses USING btree (seq DESC);


--
-- Name: market_volumes_14_mv_market_taker_maker_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX market_volumes_14_mv_market_taker_maker_type_idx ON public.market_volumes_14_mv USING btree (market, taker, maker, type);


--
-- Name: market_volumes_15_mv_market_taker_maker_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX market_volumes_15_mv_market_taker_maker_type_idx ON public.market_volumes_15_mv USING btree (market, taker, maker, type);


--
-- Name: market_volumes_180_mv_market_taker_maker_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX market_volumes_180_mv_market_taker_maker_type_idx ON public.market_volumes_180_mv USING btree (market, taker, maker, type);


--
-- Name: market_volumes_1_mv_market_taker_maker_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX market_volumes_1_mv_market_taker_maker_type_idx ON public.market_volumes_1_mv USING btree (market, taker, maker, type);


--
-- Name: market_volumes_2_mv_market_taker_maker_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX market_volumes_2_mv_market_taker_maker_type_idx ON public.market_volumes_2_mv USING btree (market, taker, maker, type);


--
-- Name: market_volumes_30_mv_market_taker_maker_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX market_volumes_30_mv_market_taker_maker_type_idx ON public.market_volumes_30_mv USING btree (market, taker, maker, type);


--
-- Name: market_volumes_365_mv_market_taker_maker_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX market_volumes_365_mv_market_taker_maker_type_idx ON public.market_volumes_365_mv USING btree (market, taker, maker, type);


--
-- Name: market_volumes_3_mv_market_taker_maker_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX market_volumes_3_mv_market_taker_maker_type_idx ON public.market_volumes_3_mv USING btree (market, taker, maker, type);


--
-- Name: market_volumes_60_mv_market_taker_maker_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX market_volumes_60_mv_market_taker_maker_type_idx ON public.market_volumes_60_mv USING btree (market, taker, maker, type);


--
-- Name: market_volumes_7_mv_market_taker_maker_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX market_volumes_7_mv_market_taker_maker_type_idx ON public.market_volumes_7_mv USING btree (market, taker, maker, type);


--
-- Name: market_volumes_90_mv_market_taker_maker_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX market_volumes_90_mv_market_taker_maker_type_idx ON public.market_volumes_90_mv USING btree (market, taker, maker, type);


--
-- Name: market_volumes_from_2023_mv_market_taker_maker_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX market_volumes_from_2023_mv_market_taker_maker_type_idx ON public.market_volumes_from_2023_mv USING btree (market, taker, maker, type);


--
-- Name: memos_md5_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX memos_md5_idx ON public.memos USING btree (md5(memo));


--
-- Name: mirror_mints_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX mirror_mints_block_num_idx ON public.mirror_mints USING btree (block_num);


--
-- Name: mirror_mints_result_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX mirror_mints_result_id_idx ON public.mirror_mints USING btree (result_id);


--
-- Name: mirror_mints_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX mirror_mints_seq_idx ON public.mirror_mints USING btree (seq DESC);


--
-- Name: mirror_results_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX mirror_results_block_num_idx ON public.mirror_results USING btree (block_num);


--
-- Name: mirror_results_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX mirror_results_seq_idx ON public.mirror_results USING btree (seq DESC);


--
-- Name: mirror_swap_mints_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX mirror_swap_mints_block_num_idx ON public.mirror_swap_mints USING btree (block_num);


--
-- Name: mirror_swap_mints_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX mirror_swap_mints_seq_idx ON public.mirror_swap_mints USING btree (seq DESC);


--
-- Name: monthly_collection_volume_mv_to_date_collection_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX monthly_collection_volume_mv_to_date_collection_type_idx ON public.monthly_collection_volume_mv USING btree (to_date, collection, type);


--
-- Name: names_name_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX names_name_idx ON public.names USING btree (name);


--
-- Name: nft_hive_actions_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX nft_hive_actions_seq_idx ON public.nft_hive_actions USING btree (seq DESC);


--
-- Name: notification_users_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX notification_users_block_num_idx ON public.notification_users USING btree (block_num);


--
-- Name: notification_users_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX notification_users_seq_idx ON public.notification_users USING btree (seq DESC);


--
-- Name: notifications_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX notifications_seq_idx ON public.notifications USING btree (seq DESC);


--
-- Name: pack_updates_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX pack_updates_block_num_idx ON public.pack_updates USING btree (block_num);


--
-- Name: pack_updates_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX pack_updates_seq_idx ON public.pack_updates USING btree (seq DESC);


--
-- Name: packs_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX packs_block_num_idx ON public.packs USING btree (block_num);


--
-- Name: packs_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX packs_seq_idx ON public.packs USING btree (seq DESC);


--
-- Name: packs_template_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX packs_template_id_idx ON public.packs USING btree (template_id);


--
-- Name: personal_blacklist_actions_mv_account_collection_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX personal_blacklist_actions_mv_account_collection_seq_idx ON public.personal_blacklist_actions_mv USING btree (account, collection, seq DESC);


--
-- Name: personal_blacklist_actions_mv_account_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX personal_blacklist_actions_mv_account_idx ON public.personal_blacklist_actions_mv USING btree (account);


--
-- Name: personal_blacklist_mv_account_collection_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX personal_blacklist_mv_account_collection_idx ON public.personal_blacklist_mv USING btree (account, collection);


--
-- Name: pfp_assets_attribute_ids_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX pfp_assets_attribute_ids_idx ON public.pfp_assets USING gin (attribute_ids);


--
-- Name: pfp_assets_collection_schema_asset_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX pfp_assets_collection_schema_asset_id_idx ON public.pfp_assets USING btree (collection, schema, asset_id);


--
-- Name: pfp_drop_data_drop_id_contract_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX pfp_drop_data_drop_id_contract_idx ON public.pfp_drop_data USING btree (drop_id, contract);


--
-- Name: pfp_mints_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX pfp_mints_block_num_idx ON public.pfp_mints USING btree (block_num);


--
-- Name: pfp_mints_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX pfp_mints_seq_idx ON public.pfp_mints USING btree (seq DESC);


--
-- Name: pfp_results_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX pfp_results_block_num_idx ON public.pfp_results USING btree (block_num);


--
-- Name: pfp_results_drop_id_result_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX pfp_results_drop_id_result_id_idx ON public.pfp_results USING btree (drop_id, result_id);


--
-- Name: pfp_results_result_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX pfp_results_result_id_idx ON public.pfp_results USING btree (result_id);


--
-- Name: pfp_results_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX pfp_results_seq_idx ON public.pfp_results USING btree (seq DESC);


--
-- Name: pfp_swap_mints_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX pfp_swap_mints_block_num_idx ON public.pfp_swap_mints USING btree (block_num);


--
-- Name: pfp_swap_mints_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX pfp_swap_mints_seq_idx ON public.pfp_swap_mints USING btree (seq DESC);


--
-- Name: pfp_swap_results_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX pfp_swap_results_block_num_idx ON public.pfp_swap_results USING btree (block_num);


--
-- Name: pfp_swap_results_drop_id_result_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX pfp_swap_results_drop_id_result_id_idx ON public.pfp_swap_results USING btree (drop_id, result_id);


--
-- Name: pfp_swap_results_result_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX pfp_swap_results_result_id_idx ON public.pfp_swap_results USING btree (result_id);


--
-- Name: pfp_swap_results_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX pfp_swap_results_seq_idx ON public.pfp_swap_results USING btree (seq DESC);


--
-- Name: pfp_templates_template_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX pfp_templates_template_id_idx ON public.pfp_templates USING btree (template_id);


--
-- Name: pool_assets_asset_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX pool_assets_asset_id_idx ON public.pool_assets USING btree (asset_id);


--
-- Name: pool_assets_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX pool_assets_block_num_idx ON public.pool_assets USING btree (block_num);


--
-- Name: pool_assets_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX pool_assets_seq_idx ON public.pool_assets USING btree (seq DESC);


--
-- Name: pool_deletions_asset_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX pool_deletions_asset_id_idx ON public.pool_deletions USING btree (asset_id);


--
-- Name: pool_deletions_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX pool_deletions_block_num_idx ON public.pool_deletions USING btree (block_num);


--
-- Name: pool_deletions_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX pool_deletions_seq_idx ON public.pool_deletions USING btree (seq DESC);


--
-- Name: purchased_atomic_listings_sale_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX purchased_atomic_listings_sale_id_idx ON public.purchased_atomic_listings USING btree (sale_id);


--
-- Name: purchased_atomic_listings_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX purchased_atomic_listings_seq_idx ON public.purchased_atomic_listings USING btree (seq DESC);


--
-- Name: recently_sold_day_mv_template_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX recently_sold_day_mv_template_id_idx ON public.recently_sold_day_mv USING btree (template_id);


--
-- Name: recently_sold_hour_mv_template_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX recently_sold_hour_mv_template_id_idx ON public.recently_sold_hour_mv USING btree (template_id);


--
-- Name: recently_sold_month_mv_template_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX recently_sold_month_mv_template_id_idx ON public.recently_sold_month_mv USING btree (template_id);


--
-- Name: recently_sold_week_mv_template_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX recently_sold_week_mv_template_id_idx ON public.recently_sold_week_mv USING btree (template_id);


--
-- Name: removed_atomic_listings_removed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_atomic_listings_removed_block_num_idx ON public.removed_atomic_listings USING btree (removed_block_num);


--
-- Name: removed_atomic_listings_removed_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_atomic_listings_removed_seq_idx ON public.removed_atomic_listings USING btree (removed_seq);


--
-- Name: removed_atomicasset_offers_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_atomicasset_offers_block_num_idx ON public.removed_atomicassets_offers USING btree (block_num);


--
-- Name: removed_atomicasset_offers_offer_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_atomicasset_offers_offer_id_idx ON public.removed_atomicassets_offers USING btree (offer_id);


--
-- Name: removed_atomicasset_offers_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_atomicasset_offers_seq_idx ON public.removed_atomicassets_offers USING btree (seq DESC);


--
-- Name: removed_atomicassets_offers_removed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_atomicassets_offers_removed_block_num_idx ON public.removed_atomicassets_offers USING btree (removed_block_num);


--
-- Name: removed_atomicmarket_auctions_removed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_atomicmarket_auctions_removed_block_num_idx ON public.removed_atomicmarket_auctions USING btree (removed_block_num);


--
-- Name: removed_atomicmarket_auctions_removed_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_atomicmarket_auctions_removed_seq_idx ON public.removed_atomicmarket_auctions USING btree (removed_seq DESC);


--
-- Name: removed_atomicmarket_buy_offers_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_atomicmarket_buy_offers_block_num_idx ON public.removed_atomicmarket_buy_offers USING btree (block_num);


--
-- Name: removed_atomicmarket_buy_offers_buyoffer_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_atomicmarket_buy_offers_buyoffer_id_idx ON public.removed_atomicmarket_buy_offers USING btree (buyoffer_id);


--
-- Name: removed_atomicmarket_buy_offers_removed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_atomicmarket_buy_offers_removed_block_num_idx ON public.removed_atomicmarket_buy_offers USING btree (removed_block_num);


--
-- Name: removed_atomicmarket_buy_offers_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_atomicmarket_buy_offers_seq_idx ON public.removed_atomicmarket_buy_offers USING btree (seq DESC);


--
-- Name: removed_atomicmarket_template_buy_offers_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_atomicmarket_template_buy_offers_block_num_idx ON public.removed_atomicmarket_template_buy_offers USING btree (block_num);


--
-- Name: removed_atomicmarket_template_buy_offers_buyoffer_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX removed_atomicmarket_template_buy_offers_buyoffer_id_idx ON public.removed_atomicmarket_template_buy_offers USING btree (buyoffer_id);


--
-- Name: removed_atomicmarket_template_buy_offers_removed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_atomicmarket_template_buy_offers_removed_block_num_idx ON public.removed_atomicmarket_template_buy_offers USING btree (removed_block_num);


--
-- Name: removed_atomicmarket_template_buy_offers_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_atomicmarket_template_buy_offers_seq_idx ON public.removed_atomicmarket_template_buy_offers USING btree (seq DESC);


--
-- Name: removed_favorites_removed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_favorites_removed_block_num_idx ON public.removed_favorites USING btree (removed_block_num);


--
-- Name: removed_follows_removed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_follows_removed_block_num_idx ON public.removed_follows USING btree (removed_block_num);


--
-- Name: removed_notification_users_removed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_notification_users_removed_block_num_idx ON public.removed_notification_users USING btree (removed_block_num);


--
-- Name: removed_pool_assets_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_pool_assets_block_num_idx ON public.removed_pool_assets USING btree (block_num);


--
-- Name: removed_pool_assets_removed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_pool_assets_removed_block_num_idx ON public.removed_pool_assets USING btree (removed_block_num);


--
-- Name: removed_pool_assets_removed_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_pool_assets_removed_seq_idx ON public.removed_pool_assets USING btree (removed_seq);


--
-- Name: removed_pool_assets_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_pool_assets_seq_idx ON public.removed_pool_assets USING btree (seq DESC);


--
-- Name: removed_pools_removed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_pools_removed_block_num_idx ON public.removed_pools USING btree (removed_block_num);


--
-- Name: removed_rwax_tokenizations_removed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_rwax_tokenizations_removed_block_num_idx ON public.removed_rwax_tokenizations USING btree (removed_block_num);


--
-- Name: removed_rwax_tokenizations_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_rwax_tokenizations_seq_idx ON public.removed_rwax_tokenizations USING btree (seq DESC);


--
-- Name: removed_rwax_tokens_removed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_rwax_tokens_removed_block_num_idx ON public.removed_rwax_tokens USING btree (removed_block_num);


--
-- Name: removed_rwax_tokens_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_rwax_tokens_seq_idx ON public.removed_rwax_tokens USING btree (seq DESC);


--
-- Name: removed_simplemarket_listings_removed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_simplemarket_listings_removed_block_num_idx ON public.removed_simplemarket_listings USING btree (removed_block_num);


--
-- Name: removed_simplemarket_listings_removed_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_simplemarket_listings_removed_seq_idx ON public.removed_simplemarket_listings USING btree (removed_seq DESC);


--
-- Name: removed_simplemarket_listings_sale_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_simplemarket_listings_sale_id_idx ON public.removed_simplemarket_listings USING btree (sale_id);


--
-- Name: removed_stakes_removed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_stakes_removed_block_num_idx ON public.removed_stakes USING btree (removed_block_num);


--
-- Name: removed_waxplorercom_listings_removed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_waxplorercom_listings_removed_block_num_idx ON public.removed_waxplorercom_listings USING btree (removed_block_num);


--
-- Name: removed_waxplorercom_listings_sale_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_waxplorercom_listings_sale_id_idx ON public.removed_waxplorercom_listings USING btree (sale_id);


--
-- Name: removed_wuffi_airdrops_removed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX removed_wuffi_airdrops_removed_block_num_idx ON public.removed_wuffi_airdrops USING btree (removed_block_num);


--
-- Name: rwax_redemptions_asset_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX rwax_redemptions_asset_id_idx ON public.rwax_redemptions USING btree (asset_id);


--
-- Name: rwax_redemptions_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX rwax_redemptions_block_num_idx ON public.rwax_redemptions USING btree (block_num);


--
-- Name: rwax_redemptions_contract_symbol_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX rwax_redemptions_contract_symbol_idx ON public.rwax_redemptions USING btree (contract, symbol);


--
-- Name: rwax_redemptions_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX rwax_redemptions_seq_idx ON public.rwax_redemptions USING btree (seq DESC);


--
-- Name: rwax_templates_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX rwax_templates_block_num_idx ON public.rwax_templates USING btree (block_num);


--
-- Name: rwax_templates_contract_symbol_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX rwax_templates_contract_symbol_idx ON public.rwax_templates USING btree (contract, symbol);


--
-- Name: rwax_templates_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX rwax_templates_seq_idx ON public.rwax_templates USING btree (seq DESC);


--
-- Name: rwax_tokenizations_asset_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX rwax_tokenizations_asset_id_idx ON public.rwax_tokenizations USING btree (asset_id);


--
-- Name: rwax_tokenizations_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX rwax_tokenizations_block_num_idx ON public.rwax_tokenizations USING btree (block_num);


--
-- Name: rwax_tokenizations_contract_symbol_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX rwax_tokenizations_contract_symbol_idx ON public.rwax_tokenizations USING btree (contract, symbol);


--
-- Name: rwax_tokenizations_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX rwax_tokenizations_seq_idx ON public.rwax_tokenizations USING btree (seq DESC);


--
-- Name: rwax_tokens_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX rwax_tokens_block_num_idx ON public.rwax_tokens USING btree (block_num);


--
-- Name: rwax_tokens_contract_symbol_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX rwax_tokens_contract_symbol_idx ON public.rwax_tokens USING btree (contract, symbol);


--
-- Name: rwax_tokens_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX rwax_tokens_seq_idx ON public.rwax_tokens USING btree (seq DESC);


--
-- Name: sales_asset_ids_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX sales_asset_ids_idx ON public.sales USING gin (asset_ids);


--
-- Name: sales_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX sales_block_num_idx ON public.sales USING btree (block_num);


--
-- Name: sales_buyer_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX sales_buyer_idx ON public.sales USING btree (buyer);


--
-- Name: sales_seller_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX sales_seller_idx ON public.sales USING btree (seller);


--
-- Name: sales_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX sales_seq_idx ON public.sales USING btree (seq DESC);


--
-- Name: sales_seven_day_chart_mv_collection_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX sales_seven_day_chart_mv_collection_type_idx ON public.sales_seven_day_chart_mv USING btree (collection, type);


--
-- Name: sales_summary_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX sales_summary_block_num_idx ON public.sales_summary USING btree (block_num);


--
-- Name: sales_summary_buyer_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX sales_summary_buyer_idx ON public.sales_summary USING btree (buyer);


--
-- Name: sales_summary_collection_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX sales_summary_collection_idx ON public.sales_summary USING btree (collection);


--
-- Name: sales_summary_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX sales_summary_seq_idx ON public.sales_summary USING btree (seq DESC);


--
-- Name: sales_summary_timestamp_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX sales_summary_timestamp_idx ON public.sales_summary USING btree ("timestamp" DESC);


--
-- Name: sales_summary_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX sales_summary_type_idx ON public.sales_summary USING btree (type);


--
-- Name: sales_summary_type_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX sales_summary_type_seq_idx ON public.sales_summary USING btree (type, seq DESC);


--
-- Name: sales_timestamp_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX sales_timestamp_idx ON public.sales USING btree ("timestamp" DESC);


--
-- Name: sales_usd_price_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX sales_usd_price_idx ON public.sales USING btree (usd_price DESC);


--
-- Name: sales_wax_price_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX sales_wax_price_idx ON public.sales USING btree (wax_price DESC);


--
-- Name: schema_stats_mv_collection_schema_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX schema_stats_mv_collection_schema_idx ON public.schema_stats_mv USING btree (collection, schema);


--
-- Name: schemas_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX schemas_block_num_idx ON public.schemas USING btree (block_num);


--
-- Name: schemas_collection_schema_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX schemas_collection_schema_idx ON public.schemas USING btree (collection, schema);


--
-- Name: schemas_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX schemas_seq_idx ON public.schemas USING btree (seq DESC);


--
-- Name: secondary_market_sales_asset_ids_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX secondary_market_sales_asset_ids_idx ON public.market_myth_sales USING gin (asset_ids);


--
-- Name: secondary_market_sales_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX secondary_market_sales_block_num_idx ON public.market_myth_sales USING btree (block_num);


--
-- Name: secondary_market_sales_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX secondary_market_sales_seq_idx ON public.market_myth_sales USING btree (seq DESC);


--
-- Name: seller_volumes_mv_user_name_collection_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX seller_volumes_mv_user_name_collection_type_idx ON public.seller_volumes_mv USING btree (user_name, collection, type);


--
-- Name: simpleassets_burns_asset_ids_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX simpleassets_burns_asset_ids_idx ON public.simpleassets_burns USING gin (asset_ids);


--
-- Name: simpleassets_burns_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX simpleassets_burns_block_num_idx ON public.simpleassets_burns USING btree (block_num);


--
-- Name: simpleassets_burns_reversed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX simpleassets_burns_reversed_block_num_idx ON public.simpleassets_burns_reversed USING btree (block_num DESC);


--
-- Name: simpleassets_burns_reversed_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX simpleassets_burns_reversed_seq_idx ON public.simpleassets_burns_reversed USING btree (seq);


--
-- Name: simpleassets_burns_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX simpleassets_burns_seq_idx ON public.simpleassets_burns USING btree (seq DESC);


--
-- Name: simpleassets_burns_unnested_asset_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX simpleassets_burns_unnested_asset_id_idx ON public.simpleassets_burns_unnested USING btree (asset_id);


--
-- Name: simpleassets_claims_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX simpleassets_claims_block_num_idx ON public.simpleassets_claims USING btree (block_num);


--
-- Name: simpleassets_claims_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX simpleassets_claims_seq_idx ON public.simpleassets_claims USING btree (seq DESC);


--
-- Name: simpleassets_offers_asset_ids_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX simpleassets_offers_asset_ids_idx ON public.simpleassets_offers USING gin (asset_ids);


--
-- Name: simpleassets_offers_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX simpleassets_offers_block_num_idx ON public.simpleassets_offers USING btree (block_num);


--
-- Name: simpleassets_offers_owner_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX simpleassets_offers_owner_idx ON public.simpleassets_offers USING btree (owner);


--
-- Name: simpleassets_offers_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX simpleassets_offers_seq_idx ON public.simpleassets_offers USING btree (seq DESC);


--
-- Name: simpleassets_updates_asset_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX simpleassets_updates_asset_id_idx ON public.simpleassets_updates USING btree (asset_id);


--
-- Name: simpleassets_updates_asset_id_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX simpleassets_updates_asset_id_idx1 ON public.simpleassets_updates USING btree (asset_id) WHERE (NOT applied);


--
-- Name: simpleassets_updates_asset_id_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX simpleassets_updates_asset_id_seq_idx ON public.simpleassets_updates USING btree (asset_id, seq) WHERE (NOT applied);


--
-- Name: simpleassets_updates_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX simpleassets_updates_block_num_idx ON public.simpleassets_updates USING btree (block_num);


--
-- Name: simpleassets_updates_max_seqs_asset_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX simpleassets_updates_max_seqs_asset_id_idx ON public.simpleassets_updates_max_seqs USING btree (asset_id);


--
-- Name: simpleassets_updates_reversed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX simpleassets_updates_reversed_block_num_idx ON public.simpleassets_updates_reversed USING btree (block_num);


--
-- Name: simpleassets_updates_reversed_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX simpleassets_updates_reversed_seq_idx ON public.simpleassets_updates_reversed USING btree (seq DESC);


--
-- Name: simpleassets_updates_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX simpleassets_updates_seq_idx ON public.simpleassets_updates USING btree (seq DESC);


--
-- Name: simpleassets_updates_seq_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX simpleassets_updates_seq_idx1 ON public.simpleassets_updates USING btree (seq) WHERE (NOT applied);


--
-- Name: simplemarket_buylogs_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX simplemarket_buylogs_seq_idx ON public.simplemarket_buylogs USING btree (seq DESC);


--
-- Name: simplemarket_cancels_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX simplemarket_cancels_block_num_idx ON public.simplemarket_cancels USING btree (block_num);


--
-- Name: simplemarket_cancels_owner_asset_ids_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX simplemarket_cancels_owner_asset_ids_idx ON public.simplemarket_cancels USING btree (owner, asset_ids);


--
-- Name: simplemarket_cancels_owner_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX simplemarket_cancels_owner_idx ON public.simplemarket_cancels USING btree (owner);


--
-- Name: simplemarket_cancels_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX simplemarket_cancels_seq_idx ON public.simplemarket_cancels USING btree (seq DESC);


--
-- Name: simplemarket_purchases_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX simplemarket_purchases_block_num_idx ON public.simplemarket_purchases USING btree (block_num);


--
-- Name: simplemarket_purchases_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX simplemarket_purchases_seq_idx ON public.simplemarket_purchases USING btree (seq DESC);


--
-- Name: simplemarket_updates_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX simplemarket_updates_block_num_idx ON public.simplemarket_updates USING btree (block_num);


--
-- Name: simplemarket_updates_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX simplemarket_updates_seq_idx ON public.simplemarket_updates USING btree (seq DESC);


--
-- Name: sold_atomicmarket_template_buy_offers_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX sold_atomicmarket_template_buy_offers_block_num_idx ON public.sold_atomicmarket_template_buy_offers USING btree (block_num);


--
-- Name: sold_atomicmarket_template_buy_offers_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX sold_atomicmarket_template_buy_offers_seq_idx ON public.sold_atomicmarket_template_buy_offers USING btree (seq DESC);


--
-- Name: stakes_asset_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX stakes_asset_id_idx ON public.stakes USING btree (asset_id);


--
-- Name: stakes_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX stakes_block_num_idx ON public.stakes USING btree (block_num);


--
-- Name: stakes_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX stakes_seq_idx ON public.stakes USING btree (seq DESC);


--
-- Name: tag_filter_actions_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX tag_filter_actions_block_num_idx ON public.tag_filter_actions USING btree (block_num);


--
-- Name: tag_filter_actions_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX tag_filter_actions_seq_idx ON public.tag_filter_actions USING btree (seq DESC);


--
-- Name: tag_filter_actions_user_name_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX tag_filter_actions_user_name_seq_idx ON public.tag_filter_actions USING btree (user_name, seq DESC);


--
-- Name: tag_filters_mv_user_name_tag_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX tag_filters_mv_user_name_tag_id_idx ON public.tag_filters_mv USING btree (user_name, tag_id);


--
-- Name: tag_updates_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX tag_updates_block_num_idx ON public.tag_updates USING btree (block_num);


--
-- Name: tag_updates_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX tag_updates_seq_idx ON public.tag_updates USING btree (seq DESC);


--
-- Name: tags_mv_collection_tag_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX tags_mv_collection_tag_id_idx ON public.tags_mv USING btree (collection, tag_id);


--
-- Name: template_collection_sales_by_date_befor_template_id_to_date_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX template_collection_sales_by_date_befor_template_id_to_date_idx ON public.template_collection_sales_by_date_before_2024_mv USING btree (template_id, to_date DESC);


--
-- Name: template_collection_sales_by_date_from__template_id_to_date_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX template_collection_sales_by_date_from__template_id_to_date_idx ON public.template_collection_sales_by_date_from_2024_mv USING btree (template_id, to_date DESC);


--
-- Name: template_collection_sales_by_date_mv_template_id_to_date_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX template_collection_sales_by_date_mv_template_id_to_date_idx ON public.template_collection_sales_by_date_mv USING btree (template_id, to_date DESC);


--
-- Name: template_floor_prices_mv_floor_price_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX template_floor_prices_mv_floor_price_idx ON public.template_floor_prices_mv USING btree (floor_price);


--
-- Name: template_floor_prices_mv_floor_price_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX template_floor_prices_mv_floor_price_idx1 ON public.template_floor_prices_mv USING btree (floor_price DESC);


--
-- Name: template_floor_prices_mv_template_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX template_floor_prices_mv_template_id_idx ON public.template_floor_prices_mv USING btree (template_id);


--
-- Name: template_sales_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX template_sales_block_num_idx ON public.template_sales USING btree (block_num);


--
-- Name: template_sales_collection_schema_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX template_sales_collection_schema_seq_idx ON public.template_sales USING btree (collection, schema, seq DESC);


--
-- Name: template_sales_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX template_sales_seq_idx ON public.template_sales USING btree (seq DESC);


--
-- Name: template_sales_template_id_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX template_sales_template_id_seq_idx ON public.template_sales USING btree (template_id, seq DESC);


--
-- Name: template_sales_template_id_usd_price_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX template_sales_template_id_usd_price_idx ON public.template_sales USING btree (template_id, usd_price DESC);


--
-- Name: template_sales_timestamp_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX template_sales_timestamp_idx ON public.template_sales USING btree ("timestamp" DESC);


--
-- Name: template_sales_usd_price_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX template_sales_usd_price_idx ON public.template_sales USING btree (usd_price DESC);


--
-- Name: template_stats_mv_template_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX template_stats_mv_template_id_idx ON public.template_stats_mv USING btree (template_id);


--
-- Name: templates_attribute_ids_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX templates_attribute_ids_idx ON public.templates USING gin (attribute_ids);


--
-- Name: templates_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX templates_block_num_idx ON public.templates USING btree (block_num);


--
-- Name: templates_collection_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX templates_collection_idx ON public.templates USING btree (collection);


--
-- Name: templates_collection_schema_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX templates_collection_schema_idx ON public.templates USING btree (collection, schema);


--
-- Name: templates_minted_mv_template_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX templates_minted_mv_template_id_idx ON public.templates_minted_mv USING btree (template_id);


--
-- Name: templates_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX templates_seq_idx ON public.templates USING btree (seq DESC);


--
-- Name: token_updates_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX token_updates_block_num_idx ON public.token_updates USING btree (block_num);


--
-- Name: token_updates_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX token_updates_seq_idx ON public.token_updates USING btree (seq DESC);


--
-- Name: tokens_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX tokens_block_num_idx ON public.tokens USING btree (block_num);


--
-- Name: tokens_contract_symbol_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX tokens_contract_symbol_idx ON public.tokens USING btree (contract, symbol);


--
-- Name: tokens_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX tokens_seq_idx ON public.tokens USING btree (seq DESC);


--
-- Name: transaction_ids_hash_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX transaction_ids_hash_idx ON public.transaction_ids USING btree (hash);


--
-- Name: transactions_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX transactions_block_num_idx ON public.transactions USING btree (block_num);


--
-- Name: transactions_transaction_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX transactions_transaction_id_idx ON public.transactions USING btree (transaction_id);


--
-- Name: transfers_asset_ids_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX transfers_asset_ids_idx ON public.transfers USING gin (asset_ids);


--
-- Name: transfers_reversed_applied_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX transfers_reversed_applied_idx ON public.transfers_reversed USING btree (applied) WHERE (NOT applied);


--
-- Name: transfers_reversed_asset_ids_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX transfers_reversed_asset_ids_idx ON public.transfers_reversed USING gin (asset_ids);


--
-- Name: transfers_reversed_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX transfers_reversed_block_num_idx ON public.transfers_reversed USING btree (block_num);


--
-- Name: transfers_reversed_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX transfers_reversed_seq_idx ON public.transfers_reversed USING btree (seq DESC);


--
-- Name: transfers_timestamp_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX transfers_timestamp_idx ON public.transfers USING btree ("timestamp" DESC);


--
-- Name: twitch_claims_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX twitch_claims_block_num_idx ON public.twitch_claims USING btree (block_num);


--
-- Name: twitch_claims_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX twitch_claims_seq_idx ON public.twitch_claims USING btree (seq DESC);


--
-- Name: twitch_drops_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX twitch_drops_block_num_idx ON public.twitch_drops USING btree (block_num);


--
-- Name: twitch_drops_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX twitch_drops_seq_idx ON public.twitch_drops USING btree (seq DESC);


--
-- Name: usd_prices_timestamp_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX usd_prices_timestamp_idx ON public.usd_prices USING btree ("timestamp" DESC);


--
-- Name: usd_prices_timestamp_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX usd_prices_timestamp_idx1 ON public.usd_prices USING btree ("timestamp" DESC);


--
-- Name: user_collection_volumes_14_mv_collection_buyer_seller_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX user_collection_volumes_14_mv_collection_buyer_seller_type_idx ON public.user_collection_volumes_14_mv USING btree (collection, buyer, seller, type);


--
-- Name: user_collection_volumes_14_mv_collection_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX user_collection_volumes_14_mv_collection_idx ON public.user_collection_volumes_14_mv USING btree (collection);


--
-- Name: user_collection_volumes_15_mv_collection_buyer_seller_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX user_collection_volumes_15_mv_collection_buyer_seller_type_idx ON public.user_collection_volumes_15_mv USING btree (collection, buyer, seller, type);


--
-- Name: user_collection_volumes_15_mv_collection_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX user_collection_volumes_15_mv_collection_idx ON public.user_collection_volumes_15_mv USING btree (collection);


--
-- Name: user_collection_volumes_180_mv_collection_buyer_seller_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX user_collection_volumes_180_mv_collection_buyer_seller_type_idx ON public.user_collection_volumes_180_mv USING btree (collection, buyer, seller, type);


--
-- Name: user_collection_volumes_180_mv_collection_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX user_collection_volumes_180_mv_collection_idx ON public.user_collection_volumes_180_mv USING btree (collection);


--
-- Name: user_collection_volumes_1_mv_collection_buyer_seller_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX user_collection_volumes_1_mv_collection_buyer_seller_type_idx ON public.user_collection_volumes_1_mv USING btree (collection, buyer, seller, type);


--
-- Name: user_collection_volumes_1_mv_collection_buyer_seller_type_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX user_collection_volumes_1_mv_collection_buyer_seller_type_idx1 ON public.user_collection_volumes_1_mv USING btree (collection, buyer, seller, type);


--
-- Name: user_collection_volumes_1_mv_collection_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX user_collection_volumes_1_mv_collection_idx ON public.user_collection_volumes_1_mv USING btree (collection);


--
-- Name: user_collection_volumes_2_mv_collection_buyer_seller_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX user_collection_volumes_2_mv_collection_buyer_seller_type_idx ON public.user_collection_volumes_2_mv USING btree (collection, buyer, seller, type);


--
-- Name: user_collection_volumes_2_mv_collection_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX user_collection_volumes_2_mv_collection_idx ON public.user_collection_volumes_2_mv USING btree (collection);


--
-- Name: user_collection_volumes_30_mv_collection_buyer_seller_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX user_collection_volumes_30_mv_collection_buyer_seller_type_idx ON public.user_collection_volumes_30_mv USING btree (collection, buyer, seller, type);


--
-- Name: user_collection_volumes_30_mv_collection_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX user_collection_volumes_30_mv_collection_idx ON public.user_collection_volumes_30_mv USING btree (collection);


--
-- Name: user_collection_volumes_365_mv_collection_buyer_seller_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX user_collection_volumes_365_mv_collection_buyer_seller_type_idx ON public.user_collection_volumes_365_mv USING btree (collection, buyer, seller, type);


--
-- Name: user_collection_volumes_365_mv_collection_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX user_collection_volumes_365_mv_collection_idx ON public.user_collection_volumes_365_mv USING btree (collection);


--
-- Name: user_collection_volumes_3_mv_collection_buyer_seller_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX user_collection_volumes_3_mv_collection_buyer_seller_type_idx ON public.user_collection_volumes_3_mv USING btree (collection, buyer, seller, type);


--
-- Name: user_collection_volumes_3_mv_collection_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX user_collection_volumes_3_mv_collection_idx ON public.user_collection_volumes_3_mv USING btree (collection);


--
-- Name: user_collection_volumes_60_mv_collection_buyer_seller_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX user_collection_volumes_60_mv_collection_buyer_seller_type_idx ON public.user_collection_volumes_60_mv USING btree (collection, buyer, seller, type);


--
-- Name: user_collection_volumes_60_mv_collection_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX user_collection_volumes_60_mv_collection_idx ON public.user_collection_volumes_60_mv USING btree (collection);


--
-- Name: user_collection_volumes_7_mv_collection_buyer_seller_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX user_collection_volumes_7_mv_collection_buyer_seller_type_idx ON public.user_collection_volumes_7_mv USING btree (collection, buyer, seller, type);


--
-- Name: user_collection_volumes_7_mv_collection_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX user_collection_volumes_7_mv_collection_idx ON public.user_collection_volumes_7_mv USING btree (collection);


--
-- Name: user_collection_volumes_90_mv_collection_buyer_seller_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX user_collection_volumes_90_mv_collection_buyer_seller_type_idx ON public.user_collection_volumes_90_mv USING btree (collection, buyer, seller, type);


--
-- Name: user_collection_volumes_90_mv_collection_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX user_collection_volumes_90_mv_collection_idx ON public.user_collection_volumes_90_mv USING btree (collection);


--
-- Name: user_collection_volumes_from_2023_mv_collection_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX user_collection_volumes_from_2023_mv_collection_idx ON public.user_collection_volumes_from_2023_mv USING btree (collection);


--
-- Name: user_collection_volumes_from_2_collection_buyer_seller_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX user_collection_volumes_from_2_collection_buyer_seller_type_idx ON public.user_collection_volumes_from_2023_mv USING btree (collection, buyer, seller, type);


--
-- Name: user_collection_volumes_mv_user_name_collection_type_actor_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX user_collection_volumes_mv_user_name_collection_type_actor_idx ON public.user_collection_volumes_mv USING btree (user_name, collection, type, actor);


--
-- Name: user_collection_volumes_s_mv_user_name_collection_actor_typ_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX user_collection_volumes_s_mv_user_name_collection_actor_typ_idx ON public.user_collection_volumes_s_mv USING btree (user_name, collection, actor, type);


--
-- Name: user_picture_updates_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX user_picture_updates_block_num_idx ON public.user_picture_updates USING btree (block_num);


--
-- Name: user_picture_updates_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX user_picture_updates_seq_idx ON public.user_picture_updates USING btree (seq DESC);


--
-- Name: user_picture_updates_user_name_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX user_picture_updates_user_name_seq_idx ON public.user_picture_updates USING btree (user_name, seq DESC);


--
-- Name: user_pictures_mv_user_name_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX user_pictures_mv_user_name_idx ON public.user_pictures_mv USING btree (user_name);


--
-- Name: user_volumes_mv_user_name_type_actor_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX user_volumes_mv_user_name_type_actor_idx ON public.user_volumes_mv USING btree (user_name, type, actor);


--
-- Name: user_volumes_s_mv_user_name_actor_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX user_volumes_s_mv_user_name_actor_type_idx ON public.user_volumes_s_mv USING btree (user_name, actor, type);


--
-- Name: users_mv_owner_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX users_mv_owner_idx ON public.users_mv USING btree (owner);


--
-- Name: verification_actions_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX verification_actions_block_num_idx ON public.verification_actions USING btree (block_num);


--
-- Name: verification_actions_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX verification_actions_seq_idx ON public.verification_actions USING btree (seq DESC);


--
-- Name: videos_video_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX videos_video_idx ON public.videos USING btree (video);


--
-- Name: volume_buyer_14_days_mv_buyer_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_buyer_14_days_mv_buyer_type_idx ON public.volume_buyer_14_days_mv USING btree (buyer, type);


--
-- Name: volume_buyer_15_days_mv_buyer_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_buyer_15_days_mv_buyer_type_idx ON public.volume_buyer_15_days_mv USING btree (buyer, type);


--
-- Name: volume_buyer_180_days_mv_buyer_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_buyer_180_days_mv_buyer_type_idx ON public.volume_buyer_180_days_mv USING btree (buyer, type);


--
-- Name: volume_buyer_1_days_mv_buyer_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_buyer_1_days_mv_buyer_type_idx ON public.volume_buyer_1_days_mv USING btree (buyer, type);


--
-- Name: volume_buyer_2_days_mv_buyer_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_buyer_2_days_mv_buyer_type_idx ON public.volume_buyer_2_days_mv USING btree (buyer, type);


--
-- Name: volume_buyer_30_days_mv_buyer_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_buyer_30_days_mv_buyer_type_idx ON public.volume_buyer_30_days_mv USING btree (buyer, type);


--
-- Name: volume_buyer_365_days_mv_buyer_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_buyer_365_days_mv_buyer_type_idx ON public.volume_buyer_365_days_mv USING btree (buyer, type);


--
-- Name: volume_buyer_3_days_mv_buyer_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_buyer_3_days_mv_buyer_type_idx ON public.volume_buyer_3_days_mv USING btree (buyer, type);


--
-- Name: volume_buyer_60_days_mv_buyer_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_buyer_60_days_mv_buyer_type_idx ON public.volume_buyer_60_days_mv USING btree (buyer, type);


--
-- Name: volume_buyer_7_days_mv_buyer_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_buyer_7_days_mv_buyer_type_idx ON public.volume_buyer_7_days_mv USING btree (buyer, type);


--
-- Name: volume_buyer_90_days_mv_buyer_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_buyer_90_days_mv_buyer_type_idx ON public.volume_buyer_90_days_mv USING btree (buyer, type);


--
-- Name: volume_buyer_all_time_mv_buyer_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_buyer_all_time_mv_buyer_type_idx ON public.volume_buyer_all_time_mv USING btree (buyer, type);


--
-- Name: volume_collection_14_days_mv_collection_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_14_days_mv_collection_type_idx ON public.volume_collection_14_days_mv USING btree (collection, type);


--
-- Name: volume_collection_15_days_mv_collection_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_15_days_mv_collection_type_idx ON public.volume_collection_15_days_mv USING btree (collection, type);


--
-- Name: volume_collection_180_days_mv_collection_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_180_days_mv_collection_type_idx ON public.volume_collection_180_days_mv USING btree (collection, type);


--
-- Name: volume_collection_1_days_mv_collection_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_1_days_mv_collection_type_idx ON public.volume_collection_1_days_mv USING btree (collection, type);


--
-- Name: volume_collection_2_days_mv_collection_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_2_days_mv_collection_type_idx ON public.volume_collection_2_days_mv USING btree (collection, type);


--
-- Name: volume_collection_30_days_mv_collection_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_30_days_mv_collection_type_idx ON public.volume_collection_30_days_mv USING btree (collection, type);


--
-- Name: volume_collection_365_days_mv_collection_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_365_days_mv_collection_type_idx ON public.volume_collection_365_days_mv USING btree (collection, type);


--
-- Name: volume_collection_3_days_mv_collection_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_3_days_mv_collection_type_idx ON public.volume_collection_3_days_mv USING btree (collection, type);


--
-- Name: volume_collection_60_days_mv_collection_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_60_days_mv_collection_type_idx ON public.volume_collection_60_days_mv USING btree (collection, type);


--
-- Name: volume_collection_7_days_mv_collection_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_7_days_mv_collection_type_idx ON public.volume_collection_7_days_mv USING btree (collection, type);


--
-- Name: volume_collection_90_days_mv_collection_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_90_days_mv_collection_type_idx ON public.volume_collection_90_days_mv USING btree (collection, type);


--
-- Name: volume_collection_all_time_mv_collection_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_all_time_mv_collection_type_idx ON public.volume_collection_all_time_mv USING btree (collection, type);


--
-- Name: volume_collection_buyer_14_days_mv_collection_buyer_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_buyer_14_days_mv_collection_buyer_type_idx ON public.volume_collection_buyer_14_days_mv USING btree (collection, buyer, type);


--
-- Name: volume_collection_buyer_15_days_mv_collection_buyer_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_buyer_15_days_mv_collection_buyer_type_idx ON public.volume_collection_buyer_15_days_mv USING btree (collection, buyer, type);


--
-- Name: volume_collection_buyer_180_days_mv_collection_buyer_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_buyer_180_days_mv_collection_buyer_type_idx ON public.volume_collection_buyer_180_days_mv USING btree (collection, buyer, type);


--
-- Name: volume_collection_buyer_1_days_mv_collection_buyer_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_buyer_1_days_mv_collection_buyer_type_idx ON public.volume_collection_buyer_1_days_mv USING btree (collection, buyer, type);


--
-- Name: volume_collection_buyer_2_days_mv_collection_buyer_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_buyer_2_days_mv_collection_buyer_type_idx ON public.volume_collection_buyer_2_days_mv USING btree (collection, buyer, type);


--
-- Name: volume_collection_buyer_30_days_mv_collection_buyer_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_buyer_30_days_mv_collection_buyer_type_idx ON public.volume_collection_buyer_30_days_mv USING btree (collection, buyer, type);


--
-- Name: volume_collection_buyer_365_days_mv_collection_buyer_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_buyer_365_days_mv_collection_buyer_type_idx ON public.volume_collection_buyer_365_days_mv USING btree (collection, buyer, type);


--
-- Name: volume_collection_buyer_3_days_mv_collection_buyer_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_buyer_3_days_mv_collection_buyer_type_idx ON public.volume_collection_buyer_3_days_mv USING btree (collection, buyer, type);


--
-- Name: volume_collection_buyer_60_days_mv_collection_buyer_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_buyer_60_days_mv_collection_buyer_type_idx ON public.volume_collection_buyer_60_days_mv USING btree (collection, buyer, type);


--
-- Name: volume_collection_buyer_7_days_mv_collection_buyer_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_buyer_7_days_mv_collection_buyer_type_idx ON public.volume_collection_buyer_7_days_mv USING btree (collection, buyer, type);


--
-- Name: volume_collection_buyer_90_days_mv_collection_buyer_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_buyer_90_days_mv_collection_buyer_type_idx ON public.volume_collection_buyer_90_days_mv USING btree (collection, buyer, type);


--
-- Name: volume_collection_buyer_all_time_mv_collection_buyer_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_buyer_all_time_mv_collection_buyer_type_idx ON public.volume_collection_buyer_all_time_mv USING btree (collection, buyer, type);


--
-- Name: volume_collection_buyer_before_2024_m_collection_buyer_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_buyer_before_2024_m_collection_buyer_type_idx ON public.volume_collection_buyer_before_2024_mv USING btree (collection, buyer, type);


--
-- Name: volume_collection_buyer_from_2024_mv_collection_buyer_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_buyer_from_2024_mv_collection_buyer_type_idx ON public.volume_collection_buyer_from_2024_mv USING btree (collection, buyer, type);


--
-- Name: volume_collection_market_14_d_collection_market_maker_taker_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_market_14_d_collection_market_maker_taker_idx ON public.volume_collection_market_14_days_mv USING btree (collection, market, maker, taker, type);


--
-- Name: volume_collection_market_15_d_collection_market_maker_taker_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_market_15_d_collection_market_maker_taker_idx ON public.volume_collection_market_15_days_mv USING btree (collection, market, maker, taker, type);


--
-- Name: volume_collection_market_180__collection_market_maker_taker_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_market_180__collection_market_maker_taker_idx ON public.volume_collection_market_180_days_mv USING btree (collection, market, maker, taker, type);


--
-- Name: volume_collection_market_1_da_collection_market_maker_taker_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_market_1_da_collection_market_maker_taker_idx ON public.volume_collection_market_1_days_mv USING btree (collection, market, maker, taker, type);


--
-- Name: volume_collection_market_2_da_collection_market_maker_taker_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_market_2_da_collection_market_maker_taker_idx ON public.volume_collection_market_2_days_mv USING btree (collection, market, maker, taker, type);


--
-- Name: volume_collection_market_30_d_collection_market_maker_taker_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_market_30_d_collection_market_maker_taker_idx ON public.volume_collection_market_30_days_mv USING btree (collection, market, maker, taker, type);


--
-- Name: volume_collection_market_365__collection_market_maker_taker_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_market_365__collection_market_maker_taker_idx ON public.volume_collection_market_365_days_mv USING btree (collection, market, maker, taker, type);


--
-- Name: volume_collection_market_3_da_collection_market_maker_taker_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_market_3_da_collection_market_maker_taker_idx ON public.volume_collection_market_3_days_mv USING btree (collection, market, maker, taker, type);


--
-- Name: volume_collection_market_60_d_collection_market_maker_taker_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_market_60_d_collection_market_maker_taker_idx ON public.volume_collection_market_60_days_mv USING btree (collection, market, maker, taker, type);


--
-- Name: volume_collection_market_7_da_collection_market_maker_taker_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_market_7_da_collection_market_maker_taker_idx ON public.volume_collection_market_7_days_mv USING btree (collection, market, maker, taker, type);


--
-- Name: volume_collection_market_90_d_collection_market_maker_taker_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_market_90_d_collection_market_maker_taker_idx ON public.volume_collection_market_90_days_mv USING btree (collection, market, maker, taker, type);


--
-- Name: volume_collection_market_all__collection_market_maker_taker_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_market_all__collection_market_maker_taker_idx ON public.volume_collection_market_all_time_mv USING btree (collection, market, maker, taker, type);


--
-- Name: volume_collection_market_use_collection_market_maker_take_idx10; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_market_use_collection_market_maker_take_idx10 ON public.volume_collection_market_user_7_days_mv USING btree (collection, market, maker, taker, buyer, seller, type);


--
-- Name: volume_collection_market_use_collection_market_maker_take_idx11; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_market_use_collection_market_maker_take_idx11 ON public.volume_collection_market_user_3_days_mv USING btree (collection, market, maker, taker, buyer, seller, type);


--
-- Name: volume_collection_market_use_collection_market_maker_take_idx12; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_market_use_collection_market_maker_take_idx12 ON public.volume_collection_market_user_2_days_mv USING btree (collection, market, maker, taker, buyer, seller, type);


--
-- Name: volume_collection_market_use_collection_market_maker_take_idx13; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_market_use_collection_market_maker_take_idx13 ON public.volume_collection_market_user_1_days_mv USING btree (collection, market, maker, taker, buyer, seller, type);


--
-- Name: volume_collection_market_user_all_time_mv_collection_market_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX volume_collection_market_user_all_time_mv_collection_market_idx ON public.volume_collection_market_user_all_time_mv USING btree (collection, market);


--
-- Name: volume_collection_market_user_collection_market_maker_take_idx1; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_market_user_collection_market_maker_take_idx1 ON public.volume_collection_market_user_from_2024_mv USING btree (collection, market, maker, taker, buyer, seller, type);


--
-- Name: volume_collection_market_user_collection_market_maker_take_idx2; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_market_user_collection_market_maker_take_idx2 ON public.volume_collection_market_user_all_time_mv USING btree (collection, market, maker, taker, buyer, seller, type);


--
-- Name: volume_collection_market_user_collection_market_maker_take_idx3; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_market_user_collection_market_maker_take_idx3 ON public.volume_collection_market_user_365_days_mv USING btree (collection, market, maker, taker, buyer, seller, type);


--
-- Name: volume_collection_market_user_collection_market_maker_take_idx4; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_market_user_collection_market_maker_take_idx4 ON public.volume_collection_market_user_180_days_mv USING btree (collection, market, maker, taker, buyer, seller, type);


--
-- Name: volume_collection_market_user_collection_market_maker_take_idx5; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_market_user_collection_market_maker_take_idx5 ON public.volume_collection_market_user_90_days_mv USING btree (collection, market, maker, taker, buyer, seller, type);


--
-- Name: volume_collection_market_user_collection_market_maker_take_idx6; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_market_user_collection_market_maker_take_idx6 ON public.volume_collection_market_user_60_days_mv USING btree (collection, market, maker, taker, buyer, seller, type);


--
-- Name: volume_collection_market_user_collection_market_maker_take_idx7; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_market_user_collection_market_maker_take_idx7 ON public.volume_collection_market_user_30_days_mv USING btree (collection, market, maker, taker, buyer, seller, type);


--
-- Name: volume_collection_market_user_collection_market_maker_take_idx8; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_market_user_collection_market_maker_take_idx8 ON public.volume_collection_market_user_15_days_mv USING btree (collection, market, maker, taker, buyer, seller, type);


--
-- Name: volume_collection_market_user_collection_market_maker_take_idx9; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_market_user_collection_market_maker_take_idx9 ON public.volume_collection_market_user_14_days_mv USING btree (collection, market, maker, taker, buyer, seller, type);


--
-- Name: volume_collection_market_user_collection_market_maker_taker_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_market_user_collection_market_maker_taker_idx ON public.volume_collection_market_user_before_2024_mv USING btree (collection, market, maker, taker, buyer, seller, type);


--
-- Name: volume_collection_seller_14_days_mv_collection_seller_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_seller_14_days_mv_collection_seller_type_idx ON public.volume_collection_seller_14_days_mv USING btree (collection, seller, type);


--
-- Name: volume_collection_seller_15_days_mv_collection_seller_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_seller_15_days_mv_collection_seller_type_idx ON public.volume_collection_seller_15_days_mv USING btree (collection, seller, type);


--
-- Name: volume_collection_seller_180_days_mv_collection_seller_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_seller_180_days_mv_collection_seller_type_idx ON public.volume_collection_seller_180_days_mv USING btree (collection, seller, type);


--
-- Name: volume_collection_seller_1_days_mv_collection_seller_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_seller_1_days_mv_collection_seller_type_idx ON public.volume_collection_seller_1_days_mv USING btree (collection, seller, type);


--
-- Name: volume_collection_seller_2_days_mv_collection_seller_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_seller_2_days_mv_collection_seller_type_idx ON public.volume_collection_seller_2_days_mv USING btree (collection, seller, type);


--
-- Name: volume_collection_seller_30_days_mv_collection_seller_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_seller_30_days_mv_collection_seller_type_idx ON public.volume_collection_seller_30_days_mv USING btree (collection, seller, type);


--
-- Name: volume_collection_seller_365_days_mv_collection_seller_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_seller_365_days_mv_collection_seller_type_idx ON public.volume_collection_seller_365_days_mv USING btree (collection, seller, type);


--
-- Name: volume_collection_seller_3_days_mv_collection_seller_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_seller_3_days_mv_collection_seller_type_idx ON public.volume_collection_seller_3_days_mv USING btree (collection, seller, type);


--
-- Name: volume_collection_seller_60_days_mv_collection_seller_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_seller_60_days_mv_collection_seller_type_idx ON public.volume_collection_seller_60_days_mv USING btree (collection, seller, type);


--
-- Name: volume_collection_seller_7_days_mv_collection_seller_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_seller_7_days_mv_collection_seller_type_idx ON public.volume_collection_seller_7_days_mv USING btree (collection, seller, type);


--
-- Name: volume_collection_seller_90_days_mv_collection_seller_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_seller_90_days_mv_collection_seller_type_idx ON public.volume_collection_seller_90_days_mv USING btree (collection, seller, type);


--
-- Name: volume_collection_seller_all_time_mv_collection_seller_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_seller_all_time_mv_collection_seller_type_idx ON public.volume_collection_seller_all_time_mv USING btree (collection, seller, type);


--
-- Name: volume_collection_seller_before_2024_collection_seller_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_seller_before_2024_collection_seller_type_idx ON public.volume_collection_seller_before_2024_mv USING btree (collection, seller, type);


--
-- Name: volume_collection_seller_from_2024_m_collection_seller_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_collection_seller_from_2024_m_collection_seller_type_idx ON public.volume_collection_seller_from_2024_mv USING btree (collection, seller, type);


--
-- Name: volume_drop_14_days_mv_collection_drop_id_market_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX volume_drop_14_days_mv_collection_drop_id_market_idx ON public.volume_drop_14_days_mv USING btree (collection, drop_id, market);


--
-- Name: volume_drop_15_days_mv_collection_drop_id_market_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX volume_drop_15_days_mv_collection_drop_id_market_idx ON public.volume_drop_15_days_mv USING btree (collection, drop_id, market);


--
-- Name: volume_drop_180_days_mv_collection_drop_id_market_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX volume_drop_180_days_mv_collection_drop_id_market_idx ON public.volume_drop_180_days_mv USING btree (collection, drop_id, market);


--
-- Name: volume_drop_1_days_mv_collection_drop_id_market_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX volume_drop_1_days_mv_collection_drop_id_market_idx ON public.volume_drop_1_days_mv USING btree (collection, drop_id, market);


--
-- Name: volume_drop_2_days_mv_collection_drop_id_market_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX volume_drop_2_days_mv_collection_drop_id_market_idx ON public.volume_drop_2_days_mv USING btree (collection, drop_id, market);


--
-- Name: volume_drop_30_days_mv_collection_drop_id_market_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX volume_drop_30_days_mv_collection_drop_id_market_idx ON public.volume_drop_30_days_mv USING btree (collection, drop_id, market);


--
-- Name: volume_drop_365_days_mv_collection_drop_id_market_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX volume_drop_365_days_mv_collection_drop_id_market_idx ON public.volume_drop_365_days_mv USING btree (collection, drop_id, market);


--
-- Name: volume_drop_3_days_mv_collection_drop_id_market_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX volume_drop_3_days_mv_collection_drop_id_market_idx ON public.volume_drop_3_days_mv USING btree (collection, drop_id, market);


--
-- Name: volume_drop_60_days_mv_collection_drop_id_market_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX volume_drop_60_days_mv_collection_drop_id_market_idx ON public.volume_drop_60_days_mv USING btree (collection, drop_id, market);


--
-- Name: volume_drop_7_days_mv_collection_drop_id_market_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX volume_drop_7_days_mv_collection_drop_id_market_idx ON public.volume_drop_7_days_mv USING btree (collection, drop_id, market);


--
-- Name: volume_drop_90_days_mv_collection_drop_id_market_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX volume_drop_90_days_mv_collection_drop_id_market_idx ON public.volume_drop_90_days_mv USING btree (collection, drop_id, market);


--
-- Name: volume_drop_all_time_mv_collection_drop_id_market_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX volume_drop_all_time_mv_collection_drop_id_market_idx ON public.volume_drop_all_time_mv USING btree (collection, drop_id, market);


--
-- Name: volume_market_14_days_mv_market_maker_taker_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_market_14_days_mv_market_maker_taker_type_idx ON public.volume_market_14_days_mv USING btree (market, maker, taker, type);


--
-- Name: volume_market_15_days_mv_market_maker_taker_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_market_15_days_mv_market_maker_taker_type_idx ON public.volume_market_15_days_mv USING btree (market, maker, taker, type);


--
-- Name: volume_market_180_days_mv_market_maker_taker_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_market_180_days_mv_market_maker_taker_type_idx ON public.volume_market_180_days_mv USING btree (market, maker, taker, type);


--
-- Name: volume_market_1_days_mv_market_maker_taker_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_market_1_days_mv_market_maker_taker_type_idx ON public.volume_market_1_days_mv USING btree (market, maker, taker, type);


--
-- Name: volume_market_2_days_mv_market_maker_taker_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_market_2_days_mv_market_maker_taker_type_idx ON public.volume_market_2_days_mv USING btree (market, maker, taker, type);


--
-- Name: volume_market_30_days_mv_market_maker_taker_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_market_30_days_mv_market_maker_taker_type_idx ON public.volume_market_30_days_mv USING btree (market, maker, taker, type);


--
-- Name: volume_market_365_days_mv_market_maker_taker_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_market_365_days_mv_market_maker_taker_type_idx ON public.volume_market_365_days_mv USING btree (market, maker, taker, type);


--
-- Name: volume_market_3_days_mv_market_maker_taker_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_market_3_days_mv_market_maker_taker_type_idx ON public.volume_market_3_days_mv USING btree (market, maker, taker, type);


--
-- Name: volume_market_60_days_mv_market_maker_taker_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_market_60_days_mv_market_maker_taker_type_idx ON public.volume_market_60_days_mv USING btree (market, maker, taker, type);


--
-- Name: volume_market_7_days_mv_market_maker_taker_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_market_7_days_mv_market_maker_taker_type_idx ON public.volume_market_7_days_mv USING btree (market, maker, taker, type);


--
-- Name: volume_market_90_days_mv_market_maker_taker_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_market_90_days_mv_market_maker_taker_type_idx ON public.volume_market_90_days_mv USING btree (market, maker, taker, type);


--
-- Name: volume_market_all_time_mv_market_maker_taker_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_market_all_time_mv_market_maker_taker_type_idx ON public.volume_market_all_time_mv USING btree (market, maker, taker, type);


--
-- Name: volume_seller_14_days_mv_seller_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_seller_14_days_mv_seller_type_idx ON public.volume_seller_14_days_mv USING btree (seller, type);


--
-- Name: volume_seller_15_days_mv_seller_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_seller_15_days_mv_seller_type_idx ON public.volume_seller_15_days_mv USING btree (seller, type);


--
-- Name: volume_seller_180_days_mv_seller_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_seller_180_days_mv_seller_type_idx ON public.volume_seller_180_days_mv USING btree (seller, type);


--
-- Name: volume_seller_1_days_mv_seller_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_seller_1_days_mv_seller_type_idx ON public.volume_seller_1_days_mv USING btree (seller, type);


--
-- Name: volume_seller_2_days_mv_seller_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_seller_2_days_mv_seller_type_idx ON public.volume_seller_2_days_mv USING btree (seller, type);


--
-- Name: volume_seller_30_days_mv_seller_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_seller_30_days_mv_seller_type_idx ON public.volume_seller_30_days_mv USING btree (seller, type);


--
-- Name: volume_seller_365_days_mv_seller_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_seller_365_days_mv_seller_type_idx ON public.volume_seller_365_days_mv USING btree (seller, type);


--
-- Name: volume_seller_3_days_mv_seller_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_seller_3_days_mv_seller_type_idx ON public.volume_seller_3_days_mv USING btree (seller, type);


--
-- Name: volume_seller_60_days_mv_seller_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_seller_60_days_mv_seller_type_idx ON public.volume_seller_60_days_mv USING btree (seller, type);


--
-- Name: volume_seller_7_days_mv_seller_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_seller_7_days_mv_seller_type_idx ON public.volume_seller_7_days_mv USING btree (seller, type);


--
-- Name: volume_seller_90_days_mv_seller_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_seller_90_days_mv_seller_type_idx ON public.volume_seller_90_days_mv USING btree (seller, type);


--
-- Name: volume_seller_all_time_mv_seller_type_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_seller_all_time_mv_seller_type_idx ON public.volume_seller_all_time_mv USING btree (seller, type);


--
-- Name: volume_template_14_days_mv_template_id_schema_collection_ty_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_template_14_days_mv_template_id_schema_collection_ty_idx ON public.volume_template_14_days_mv USING btree (template_id, schema, collection, type);


--
-- Name: volume_template_15_days_mv_template_id_schema_collection_ty_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_template_15_days_mv_template_id_schema_collection_ty_idx ON public.volume_template_15_days_mv USING btree (template_id, schema, collection, type);


--
-- Name: volume_template_180_days_mv_template_id_schema_collection_t_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_template_180_days_mv_template_id_schema_collection_t_idx ON public.volume_template_180_days_mv USING btree (template_id, schema, collection, type);


--
-- Name: volume_template_1_days_mv_template_id_schema_collection_typ_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_template_1_days_mv_template_id_schema_collection_typ_idx ON public.volume_template_1_days_mv USING btree (template_id, schema, collection, type);


--
-- Name: volume_template_2_days_mv_template_id_schema_collection_typ_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_template_2_days_mv_template_id_schema_collection_typ_idx ON public.volume_template_2_days_mv USING btree (template_id, schema, collection, type);


--
-- Name: volume_template_30_days_mv_template_id_schema_collection_ty_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_template_30_days_mv_template_id_schema_collection_ty_idx ON public.volume_template_30_days_mv USING btree (template_id, schema, collection, type);


--
-- Name: volume_template_365_days_mv_template_id_schema_collection_t_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_template_365_days_mv_template_id_schema_collection_t_idx ON public.volume_template_365_days_mv USING btree (template_id, schema, collection, type);


--
-- Name: volume_template_3_days_mv_template_id_schema_collection_typ_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_template_3_days_mv_template_id_schema_collection_typ_idx ON public.volume_template_3_days_mv USING btree (template_id, schema, collection, type);


--
-- Name: volume_template_60_days_mv_template_id_schema_collection_ty_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_template_60_days_mv_template_id_schema_collection_ty_idx ON public.volume_template_60_days_mv USING btree (template_id, schema, collection, type);


--
-- Name: volume_template_7_days_mv_template_id_schema_collection_typ_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_template_7_days_mv_template_id_schema_collection_typ_idx ON public.volume_template_7_days_mv USING btree (template_id, schema, collection, type);


--
-- Name: volume_template_90_days_mv_template_id_schema_collection_ty_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_template_90_days_mv_template_id_schema_collection_ty_idx ON public.volume_template_90_days_mv USING btree (template_id, schema, collection, type);


--
-- Name: volume_template_all_time_mv_template_id_schema_collection_t_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_template_all_time_mv_template_id_schema_collection_t_idx ON public.volume_template_all_time_mv USING btree (template_id, schema, collection, type);


--
-- Name: volume_template_user_14_days__template_id_schema_collection_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_template_user_14_days__template_id_schema_collection_idx ON public.volume_template_user_14_days_mv USING btree (template_id, schema, collection, buyer, seller, type);


--
-- Name: volume_template_user_15_days__template_id_schema_collection_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_template_user_15_days__template_id_schema_collection_idx ON public.volume_template_user_15_days_mv USING btree (template_id, schema, collection, buyer, seller, type);


--
-- Name: volume_template_user_180_days_template_id_schema_collection_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_template_user_180_days_template_id_schema_collection_idx ON public.volume_template_user_180_days_mv USING btree (template_id, schema, collection, buyer, seller, type);


--
-- Name: volume_template_user_1_days_m_template_id_schema_collection_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_template_user_1_days_m_template_id_schema_collection_idx ON public.volume_template_user_1_days_mv USING btree (template_id, schema, collection, buyer, seller, type);


--
-- Name: volume_template_user_2_days_m_template_id_schema_collection_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_template_user_2_days_m_template_id_schema_collection_idx ON public.volume_template_user_2_days_mv USING btree (template_id, schema, collection, buyer, seller, type);


--
-- Name: volume_template_user_30_days__template_id_schema_collection_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_template_user_30_days__template_id_schema_collection_idx ON public.volume_template_user_30_days_mv USING btree (template_id, schema, collection, buyer, seller, type);


--
-- Name: volume_template_user_365_days_template_id_schema_collection_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_template_user_365_days_template_id_schema_collection_idx ON public.volume_template_user_365_days_mv USING btree (template_id, schema, collection, buyer, seller, type);


--
-- Name: volume_template_user_3_days_m_template_id_schema_collection_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_template_user_3_days_m_template_id_schema_collection_idx ON public.volume_template_user_3_days_mv USING btree (template_id, schema, collection, buyer, seller, type);


--
-- Name: volume_template_user_60_days__template_id_schema_collection_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_template_user_60_days__template_id_schema_collection_idx ON public.volume_template_user_60_days_mv USING btree (template_id, schema, collection, buyer, seller, type);


--
-- Name: volume_template_user_7_days_m_template_id_schema_collection_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_template_user_7_days_m_template_id_schema_collection_idx ON public.volume_template_user_7_days_mv USING btree (template_id, schema, collection, buyer, seller, type);


--
-- Name: volume_template_user_90_days__template_id_schema_collection_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_template_user_90_days__template_id_schema_collection_idx ON public.volume_template_user_90_days_mv USING btree (template_id, schema, collection, buyer, seller, type);


--
-- Name: volume_template_user_all_time_template_id_schema_collection_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_template_user_all_time_template_id_schema_collection_idx ON public.volume_template_user_all_time_mv USING btree (template_id, schema, collection, buyer, seller, type);


--
-- Name: volume_template_user_before_2_template_id_schema_collection_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_template_user_before_2_template_id_schema_collection_idx ON public.volume_template_user_before_2024_mv USING btree (template_id, schema, collection, buyer, seller, type);


--
-- Name: volume_template_user_from_202_template_id_schema_collection_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX volume_template_user_from_202_template_id_schema_collection_idx ON public.volume_template_user_from_2024_mv USING btree (template_id, schema, collection, buyer, seller, type);


--
-- Name: wuffi_airdrop_claimers_airdrop_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX wuffi_airdrop_claimers_airdrop_id_idx ON public.wuffi_airdrop_claimers USING btree (airdrop_id);


--
-- Name: wuffi_airdrop_claimers_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX wuffi_airdrop_claimers_block_num_idx ON public.wuffi_airdrop_claimers USING btree (block_num);


--
-- Name: wuffi_airdrop_claimers_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX wuffi_airdrop_claimers_seq_idx ON public.wuffi_airdrop_claimers USING btree (seq DESC);


--
-- Name: wuffi_airdrop_claims_airdrop_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX wuffi_airdrop_claims_airdrop_id_idx ON public.wuffi_airdrop_claims USING btree (airdrop_id);


--
-- Name: wuffi_airdrop_claims_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX wuffi_airdrop_claims_block_num_idx ON public.wuffi_airdrop_claims USING btree (block_num);


--
-- Name: wuffi_airdrop_claims_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX wuffi_airdrop_claims_seq_idx ON public.wuffi_airdrop_claims USING btree (seq DESC);


--
-- Name: wuffi_airdrop_data_updates_airdrop_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX wuffi_airdrop_data_updates_airdrop_id_idx ON public.wuffi_airdrop_data_updates USING btree (airdrop_id);


--
-- Name: wuffi_airdrop_data_updates_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX wuffi_airdrop_data_updates_block_num_idx ON public.wuffi_airdrop_data_updates USING btree (block_num);


--
-- Name: wuffi_airdrop_data_updates_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX wuffi_airdrop_data_updates_seq_idx ON public.wuffi_airdrop_data_updates USING btree (seq DESC);


--
-- Name: wuffi_airdrop_ready_updates_airdrop_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX wuffi_airdrop_ready_updates_airdrop_id_idx ON public.wuffi_airdrop_ready_updates USING btree (airdrop_id);


--
-- Name: wuffi_airdrop_ready_updates_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX wuffi_airdrop_ready_updates_block_num_idx ON public.wuffi_airdrop_ready_updates USING btree (block_num);


--
-- Name: wuffi_airdrop_ready_updates_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX wuffi_airdrop_ready_updates_seq_idx ON public.wuffi_airdrop_ready_updates USING btree (seq DESC);


--
-- Name: wuffi_airdrops_airdrop_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX wuffi_airdrops_airdrop_id_idx ON public.wuffi_airdrops USING btree (airdrop_id);


--
-- Name: wuffi_airdrops_block_num_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX wuffi_airdrops_block_num_idx ON public.wuffi_airdrops USING btree (block_num);


--
-- Name: wuffi_airdrops_seq_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX wuffi_airdrops_seq_idx ON public.wuffi_airdrops USING btree (seq DESC);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

GRANT ALL ON SCHEMA public TO root;


--
-- PostgreSQL database dump complete
--

