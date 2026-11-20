-- =========================================================================
-- DATABASE: agency_master
-- ARCHITECTURE: 100% Fully Autonomous AI Agent Agency (Self-Training, Self-Delegating)
-- =========================================================================

-- 1. Enable UUID Extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =========================================================================
-- SECTION A: CLIENTS & BUSINESS MASTER DATA
-- =========================================================================

-- Clients Table
CREATE TABLE IF NOT EXISTS clients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(255),
    mobile_number VARCHAR(20),
    whatsapp_number VARCHAR(20),
    email VARCHAR(255) UNIQUE,
    industry_type VARCHAR(100),
    custom_data JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Products & AI Services
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    base_price DECIMAL(10,2),
    default_agent_roles JSONB DEFAULT '[]'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Social Media Accounts
CREATE TABLE IF NOT EXISTS social_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    platform_name VARCHAR(50) NOT NULL,
    profile_url VARCHAR(255),
    encrypted_token TEXT,
    account_metadata JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Client Subscriptions
CREATE TABLE IF NOT EXISTS client_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    start_date DATE DEFAULT CURRENT_DATE,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'Active',
    custom_config JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================================
-- SECTION B: 100 LEADS OUTREACH (DAILY 5 MESSAGE BATCHING WITH FULL CONTROLS)
-- =========================================================================

-- Leads Table (Aapke 100 Mobile Numbers)
CREATE TABLE IF NOT EXISTS outreach_leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name VARCHAR(255),
    business_name VARCHAR(255),
    mobile_number VARCHAR(20) NOT NULL UNIQUE,
    whatsapp_number VARCHAR(20),
    industry VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'queued', 'contacted', 'replied', 'failed'
    notes TEXT,
    last_contacted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Dynamic Outreach Campaigns (Controls: Start, Stop, Time, Quota)
CREATE TABLE IF NOT EXISTS outreach_campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_name VARCHAR(255) NOT NULL,
    daily_quota INT DEFAULT 5, -- Daily 5 numbers
    status VARCHAR(50) DEFAULT 'Active', -- 'Active', 'Paused', 'Stopped'
    scheduled_time TIME DEFAULT '10:30:00', -- What time to trigger
    time_window_start TIME DEFAULT '10:00:00',
    time_window_end TIME DEFAULT '18:00:00',
    delay_between_messages_seconds INT DEFAULT 120, -- 2 min safety delay
    active_days JSONB DEFAULT '["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]'::jsonb,
    agent_prompt_instruction TEXT NOT NULL DEFAULT 'Aap ek professional AI Agency representative hain. Lead ka business aur name use karke ek polite aur engaging outreach message likhein.',
    channel VARCHAR(50) DEFAULT 'whatsapp',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Message Tracking Logs
CREATE TABLE IF NOT EXISTS outreach_message_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES outreach_leads(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES outreach_campaigns(id) ON DELETE CASCADE,
    agent_id UUID,
    message_content TEXT NOT NULL,
    sent_channel VARCHAR(50) DEFAULT 'whatsapp',
    sent_status VARCHAR(50) DEFAULT 'sent', -- 'sent', 'failed', 'delivered'
    response_received TEXT,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================================
-- SECTION C: SELF-EVOLVING MULTI-AGENT ORGANIZATION (NO HUMAN IN LOOP)
-- =========================================================================

-- Dynamic Agents Registry (AI Staff)
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    role VARCHAR(100) NOT NULL,
    persona TEXT NOT NULL,
    system_prompt TEXT NOT NULL,
    model_provider VARCHAR(50) DEFAULT 'gemini',
    model_name VARCHAR(100) DEFAULT 'gemini-2.5-flash',
    temperature NUMERIC(3, 2) DEFAULT 0.7,
    status VARCHAR(50) DEFAULT 'idle', -- 'idle', 'working', 'evaluating'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Autonomous Inter-Agent Tasks Board (Agents assign tasks to each other)
CREATE TABLE IF NOT EXISTS autonomous_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    objective TEXT NOT NULL,
    assigned_by VARCHAR(100) NOT NULL, -- e.g. 'CEO_Agent'
    assigned_to VARCHAR(100) NOT NULL, -- e.g. 'Outreach_Agent'
    priority VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'working', 'handed_off', 'completed', 'failed'
    input_data JSONB DEFAULT '{}'::jsonb,
    output_data JSONB DEFAULT '{}'::jsonb,
    feedback_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Dynamic Skills / Capabilities Created by Agents Autonomously
CREATE TABLE IF NOT EXISTS agent_skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    skill_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT NOT NULL,
    created_by_agent VARCHAR(100),
    execution_type VARCHAR(50) DEFAULT 'prompt_heuristic', -- 'python_tool', 'prompt_heuristic', 'api_caller'
    code_or_prompt TEXT NOT NULL,
    usage_count INT DEFAULT 0,
    success_rate NUMERIC(5, 2) DEFAULT 100.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Continuous Self-Training & Learned Knowledge Base (Auto-improvement)
CREATE TABLE IF NOT EXISTS learned_knowledge (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_role VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL, -- 'best_practice', 'mistake_to_avoid', 'conversion_pattern'
    insight TEXT NOT NULL,
    confidence_score NUMERIC(3, 2) DEFAULT 0.85,
    derived_from_task_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_leads_status ON outreach_leads(status);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON autonomous_tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned_to ON autonomous_tasks(assigned_to);
