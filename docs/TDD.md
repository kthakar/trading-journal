# Trade Blotter - Technical Design Document (TDD)

## 1. Technology Stack

### 1.1 Frontend
- Next.js 14 with App Router
- TypeScript
- State Management: React Query + Context API
- UI Library: Tailwind CSS
- Charting: Recharts
- Form Handling: React Hook Form
- Validation: Zod
- Rich Text Editor: TipTap
- Supabase Client for auth and database access

### 1.2 Backend
- Python 3.11+
- FastAPI
- Supabase Python Client
- PostgreSQL (via Supabase)
- JWT for session management
- Redis for caching
- Pydantic for data validation
- pytest for testing

### 1.3 Infrastructure
- Frontend Hosting: Vercel
- Backend Hosting: Railway
- Database & Auth: Supabase
- CI/CD: GitHub Actions
- Redis: Upstash

## 2. Database Schema

### 2.1 Users Table (Supabase Auth)
```sql
-- This is managed by Supabase Auth
-- Additional user metadata can be stored in a separate table
CREATE TABLE public.user_profiles (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    display_name TEXT,
    timezone TEXT DEFAULT 'UTC'::text
);

-- Enable RLS
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view own profile" 
    ON public.user_profiles FOR SELECT 
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" 
    ON public.user_profiles FOR UPDATE 
    USING (auth.uid() = id);
```

### 2.2 Brokerage Accounts Table
```sql
CREATE TABLE public.brokerage_accounts (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) NOT NULL,
    brokerage_type TEXT NOT NULL,
    account_id TEXT NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP WITH TIME ZONE,
    last_sync_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    UNIQUE(user_id, brokerage_type, account_id)
);

-- Enable RLS
ALTER TABLE public.brokerage_accounts ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view own brokerage accounts" 
    ON public.brokerage_accounts FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own brokerage accounts" 
    ON public.brokerage_accounts FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own brokerage accounts" 
    ON public.brokerage_accounts FOR UPDATE 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own brokerage accounts" 
    ON public.brokerage_accounts FOR DELETE 
    USING (auth.uid() = user_id);
```

### 2.3 Trades Table
```sql
CREATE TABLE public.trades (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) NOT NULL,
    brokerage_account_id UUID REFERENCES public.brokerage_accounts(id),
    symbol TEXT NOT NULL,
    entry_date TIMESTAMP WITH TIME ZONE NOT NULL,
    exit_date TIMESTAMP WITH TIME ZONE NOT NULL,
    direction TEXT NOT NULL,
    entry_price DECIMAL(10,2) NOT NULL,
    exit_price DECIMAL(10,2) NOT NULL,
    size DECIMAL(10,2) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Enable RLS
ALTER TABLE public.trades ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view own trades" 
    ON public.trades FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own trades" 
    ON public.trades FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own trades" 
    ON public.trades FOR UPDATE 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own trades" 
    ON public.trades FOR DELETE 
    USING (auth.uid() = user_id);
```

### 2.4 Journal Entries Table
```sql
CREATE TABLE public.journal_entries (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) NOT NULL,
    content TEXT NOT NULL,
    entry_date TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Enable RLS
ALTER TABLE public.journal_entries ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view own journal entries" 
    ON public.journal_entries FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own journal entries" 
    ON public.journal_entries FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own journal entries" 
    ON public.journal_entries FOR UPDATE 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own journal entries" 
    ON public.journal_entries FOR DELETE 
    USING (auth.uid() = user_id);
```

### 2.5 Journal Entry Trades Table
```sql
CREATE TABLE public.journal_entry_trades (
    journal_entry_id UUID REFERENCES public.journal_entries(id) ON DELETE CASCADE,
    trade_id UUID REFERENCES public.trades(id) ON DELETE CASCADE,
    PRIMARY KEY (journal_entry_id, trade_id)
);

-- Enable RLS
ALTER TABLE public.journal_entry_trades ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view own journal entry trades" 
    ON public.journal_entry_trades FOR SELECT 
    USING (
        EXISTS (
            SELECT 1 FROM public.journal_entries je
            WHERE je.id = journal_entry_id
            AND je.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own journal entry trades" 
    ON public.journal_entry_trades FOR INSERT 
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.journal_entries je
            WHERE je.id = journal_entry_id
            AND je.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete own journal entry trades" 
    ON public.journal_entry_trades FOR DELETE 
    USING (
        EXISTS (
            SELECT 1 FROM public.journal_entries je
            WHERE je.id = journal_entry_id
            AND je.user_id = auth.uid()
        )
    );
```

### 2.6 Tags Table
```sql
CREATE TABLE public.tags (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    UNIQUE(user_id, name)
);

-- Enable RLS
ALTER TABLE public.tags ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view own tags" 
    ON public.tags FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own tags" 
    ON public.tags FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own tags" 
    ON public.tags FOR UPDATE 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own tags" 
    ON public.tags FOR DELETE 
    USING (auth.uid() = user_id);
```

### 2.7 Trade Tags Table
```sql
CREATE TABLE public.trade_tags (
    trade_id UUID REFERENCES public.trades(id) ON DELETE CASCADE,
    tag_id UUID REFERENCES public.tags(id) ON DELETE CASCADE,
    PRIMARY KEY (trade_id, tag_id)
);

-- Enable RLS
ALTER TABLE public.trade_tags ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view own trade tags" 
    ON public.trade_tags FOR SELECT 
    USING (
        EXISTS (
            SELECT 1 FROM public.trades t
            WHERE t.id = trade_id
            AND t.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own trade tags" 
    ON public.trade_tags FOR INSERT 
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.trades t
            WHERE t.id = trade_id
            AND t.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete own trade tags" 
    ON public.trade_tags FOR DELETE 
    USING (
        EXISTS (
            SELECT 1 FROM public.trades t
            WHERE t.id = trade_id
            AND t.user_id = auth.uid()
        )
    );
```

### 2.8 Journal Entry Tags Table
```sql
CREATE TABLE public.journal_entry_tags (
    journal_entry_id UUID REFERENCES public.journal_entries(id) ON DELETE CASCADE,
    tag_id UUID REFERENCES public.tags(id) ON DELETE CASCADE,
    PRIMARY KEY (journal_entry_id, tag_id)
);

-- Enable RLS
ALTER TABLE public.journal_entry_tags ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view own journal entry tags" 
    ON public.journal_entry_tags FOR SELECT 
    USING (
        EXISTS (
            SELECT 1 FROM public.journal_entries je
            WHERE je.id = journal_entry_id
            AND je.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own journal entry tags" 
    ON public.journal_entry_tags FOR INSERT 
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.journal_entries je
            WHERE je.id = journal_entry_id
            AND je.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete own journal entry tags" 
    ON public.journal_entry_tags FOR DELETE 
    USING (
        EXISTS (
            SELECT 1 FROM public.journal_entries je
            WHERE je.id = journal_entry_id
            AND je.user_id = auth.uid()
        )
    );
```

### 2.9 Journal Entry Attachments Table
```sql
CREATE TABLE public.journal_entry_attachments (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    journal_entry_id UUID REFERENCES public.journal_entries(id) ON DELETE CASCADE,
    file_name TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    file_url TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Enable RLS
ALTER TABLE public.journal_entry_attachments ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view own journal entry attachments" 
    ON public.journal_entry_attachments FOR SELECT 
    USING (
        EXISTS (
            SELECT 1 FROM public.journal_entries je
            WHERE je.id = journal_entry_id
            AND je.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own journal entry attachments" 
    ON public.journal_entry_attachments FOR INSERT 
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.journal_entries je
            WHERE je.id = journal_entry_id
            AND je.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete own journal entry attachments" 
    ON public.journal_entry_attachments FOR DELETE 
    USING (
        EXISTS (
            SELECT 1 FROM public.journal_entries je
            WHERE je.id = journal_entry_id
            AND je.user_id = auth.uid()
        )
    );
```

## 3. API Endpoints

### 3.1 Authentication
```python
# Using Supabase Auth
# No need for custom auth endpoints as we'll use Supabase's built-in auth
```

### 3.2 Brokerage Integration
```python
# GET /api/brokerage/accounts
class GetBrokerageAccountsResponse(BaseModel):
    accounts: List[BrokerageAccount]

# POST /api/brokerage/connect
class ConnectBrokerageRequest(BaseModel):
    brokerage_type: Literal["SCHWAB", "IBKR", "TASTY"]
    account_id: str

# POST /api/brokerage/sync
class SyncBrokerageRequest(BaseModel):
    account_id: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]

# GET /api/brokerage/positions
class GetPositionsResponse(BaseModel):
    positions: List[Position]
```

### 3.3 Trades
```python
# GET /api/trades
class GetTradesResponse(BaseModel):
    trades: List[Trade]
    total: int
    page: int
    limit: int

# POST /api/trades
class CreateTradeRequest(BaseModel):
    symbol: str
    entry_date: datetime
    exit_date: datetime
    direction: Literal["LONG", "SHORT"]
    entry_price: Decimal
    exit_price: Decimal
    size: Decimal
    notes: Optional[str]
    tags: Optional[List[str]]

# GET /api/trades/:id
# PUT /api/trades/:id
# DELETE /api/trades/:id
```

### 3.4 Analytics
```python
# GET /api/analytics/summary
class AnalyticsSummary(BaseModel):
    total_trades: int
    win_rate: float
    average_win: Decimal
    average_loss: Decimal
    total_pnl: Decimal
    average_holding_time: timedelta

# GET /api/analytics/time-based
class TimeBasedAnalytics(BaseModel):
    daily: List[DailyAnalytics]
    monthly: List[MonthlyAnalytics]
    time_of_day: List[TimeOfDayAnalytics]
    day_of_week: List[DayOfWeekAnalytics]

class DailyAnalytics(BaseModel):
    date: date
    pnl: Decimal
    trades: int

class MonthlyAnalytics(BaseModel):
    month: str
    pnl: Decimal
    trades: int

class TimeOfDayAnalytics(BaseModel):
    hour: int
    pnl: Decimal
    trades: int

class DayOfWeekAnalytics(BaseModel):
    day: int
    pnl: Decimal
    trades: int

# GET /api/analytics/tags
class TagAnalytics(BaseModel):
    tag_id: UUID
    tag_name: str
    trade_count: int
    win_rate: float
    total_pnl: Decimal

# GET /api/analytics/export
# Returns CSV or JSON based on Accept header
```

### 3.5 Journal Entries
```python
# GET /api/journal-entries
class GetJournalEntriesRequest(BaseModel):
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    trade_id: Optional[UUID]
    tag_id: Optional[UUID]
    search: Optional[str]

class GetJournalEntriesResponse(BaseModel):
    entries: List[JournalEntry]
    total: int
    page: int
    limit: int

# POST /api/journal-entries
class CreateJournalEntryRequest(BaseModel):
    content: str
    entry_date: datetime
    trade_ids: Optional[List[UUID]]
    tag_ids: Optional[List[UUID]]
    attachments: Optional[List[UploadFile]]

# PUT /api/journal-entries/:id
class UpdateJournalEntryRequest(BaseModel):
    content: str
    entry_date: datetime
    trade_ids: Optional[List[UUID]]
    tag_ids: Optional[List[UUID]]
    attachments: Optional[List[UploadFile]]

# DELETE /api/journal-entries/:id

# GET /api/journal-entries/calendar
class GetJournalCalendarResponse(BaseModel):
    entries: List[CalendarEntry]

class CalendarEntry(BaseModel):
    date: date
    count: int
    has_attachments: bool

# GET /api/journal-entries/search
class SearchJournalEntriesRequest(BaseModel):
    query: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
```

### 3.6 Profile
```python
# GET /api/profile
class UserProfile(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    display_name: Optional[str]
    timezone: str

class GetProfileResponse(UserProfile):
    pass

# PUT /api/profile
class UpdateProfileRequest(BaseModel):
    display_name: Optional[str]
    timezone: Optional[str]

class UpdateProfileResponse(UserProfile):
    pass
```

## 4. Frontend Components

### 4.1 Pages
- `app/page.tsx` (Dashboard)
- `app/trades/page.tsx`
- `app/trades/[id]/page.tsx`
- `app/trades/new/page.tsx`
- `app/journal/page.tsx`
- `app/journal/[id]/page.tsx`
- `app/journal/calendar/page.tsx`
- `app/analytics/page.tsx`
- `app/brokerage/page.tsx`
- `app/settings/page.tsx`

### 4.2 Reusable Components
- `components/trades/TradeForm.tsx`
- `components/trades/TradeList.tsx`
- `components/trades/TagInput.tsx`
- `components/analytics/AnalyticsChart.tsx`
- `components/common/DateRangePicker.tsx`
- `components/common/ExportButton.tsx`
- `components/journal/JournalEditor.tsx`
- `components/journal/JournalCalendar.tsx`
- `components/journal/JournalSearch.tsx`
- `components/journal/JournalEntryList.tsx`
- `components/common/FileUpload.tsx`
- `components/brokerage/BrokerageConnect.tsx`
- `components/analytics/TimeBasedCharts.tsx`

## 5. Testing Strategy

### 5.1 Unit Tests
- Trade validation logic
- Tag management functions
- Analytics calculations
- API endpoint handlers
- Brokerage integration adapters
- Journal entry validation

### 5.2 Integration Tests
- Trade creation flow
- Tag assignment process
- Data export functionality
- Authentication flow
- Brokerage sync process
- Journal entry creation

### 5.3 E2E Tests
- Complete trade entry and analysis flow
- User registration and login
- Data export process
- Brokerage connection and sync
- Journal entry workflow

## 6. Security Considerations

### 6.1 Authentication
- Supabase Auth for authentication
- JWT token-based authentication
- Token refresh mechanism
- Rate limiting
- OAuth2 for brokerage integration

### 6.2 Data Protection
- Row Level Security (RLS) policies
- Input validation
- SQL injection prevention
- XSS protection
- CSRF protection
- Brokerage token encryption

### 6.3 API Security
- Request validation
- Error handling
- Rate limiting
- CORS configuration
- Brokerage API key management

## 7. Performance Considerations

### 7.1 Frontend
- Code splitting
- Lazy loading
- Image optimization
- Caching strategy
- Chart data optimization
- Server-side rendering where appropriate
- Static site generation for static pages
- Supabase real-time subscriptions for live updates

### 7.2 Backend
- Database indexing
- Query optimization
- Response caching
- Connection pooling
- Brokerage API rate limiting
- Async request handling
- Background task processing
- Supabase Edge Functions for serverless operations

## 8. Monitoring and Logging

### 8.1 Application Monitoring
- Error tracking
- Performance metrics
- User analytics
- API usage statistics
- Brokerage sync status
- Supabase monitoring

### 8.2 Logging
- Request logging
- Error logging
- Audit logging
- Performance logging
- Brokerage sync logging
- Supabase logs 