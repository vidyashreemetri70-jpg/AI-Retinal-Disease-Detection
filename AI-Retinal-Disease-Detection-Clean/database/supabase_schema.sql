-- =========================================================
-- RetinaScan AI - Supabase Database Schema
-- Run this entire file in: Supabase Dashboard -> SQL Editor -> New Query -> Run
-- =========================================================

-- Needed for gen_random_uuid()
create extension if not exists "pgcrypto";

-- ---------------------------------------------------------
-- 1. USERS TABLE (Doctors + Students/Patients)
-- ---------------------------------------------------------
create table if not exists users (
    id uuid primary key default gen_random_uuid(),
    full_name text not null,
    email text unique not null,
    password_hash text not null,
    role text not null check (role in ('doctor', 'student')),
    specialization text,           -- only used for doctors (e.g. Ophthalmologist)
    institution text,              -- only used for students (college/institute)
    created_at timestamptz default now()
);

create index if not exists idx_users_email on users(email);
create index if not exists idx_users_role on users(role);

-- ---------------------------------------------------------
-- 2. PREDICTIONS TABLE (every fundus image scan + result)
-- ---------------------------------------------------------
create table if not exists predictions (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references users(id) on delete cascade,
    patient_name text not null,
    patient_age int,
    patient_gender text,
    image_name text,
    predicted_class text not null,
    confidence numeric(5,2) not null,
    class_probabilities jsonb,     -- full probability breakdown for all 6 classes
    notes text,
    created_at timestamptz default now()
);

create index if not exists idx_predictions_user_id on predictions(user_id);
create index if not exists idx_predictions_created_at on predictions(created_at desc);

-- ---------------------------------------------------------
-- 3. ROW LEVEL SECURITY
-- Since auth is handled by our own Flask backend (not Supabase Auth),
-- we access these tables using the service_role key from the backend only,
-- so RLS can stay enabled with backend bypassing it via service key.
-- ---------------------------------------------------------
alter table users enable row level security;
alter table predictions enable row level security;

-- Allow the service role (used only by backend) full access.
-- (service_role key already bypasses RLS by default in Supabase,
--  these policies simply document intended access for anon/authenticated roles.)
create policy "No public access to users" on users
    for all
    using (false);

create policy "No public access to predictions" on predictions
    for all
    using (false);

-- =========================================================
-- Done. Your database is ready.
-- Tables created: users, predictions
-- =========================================================
