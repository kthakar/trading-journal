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
    token_type TEXT,
    token_expires_at TIMESTAMP WITH TIME ZONE,
    scope TEXT[],
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

class ConnectBrokerageResponse(BaseModel):
    auth_url: str
    state: str
    code_verifier: Optional[str]  # Only for PKCE flows

# GET /api/brokerage/callback
class OAuthCallbackRequest(BaseModel):
    code: str
    state: str
    brokerage_type: Literal["SCHWAB", "IBKR", "TASTY"]

# POST /api/brokerage/disconnect
class DisconnectBrokerageRequest(BaseModel):
    brokerage_type: Literal["SCHWAB", "IBKR", "TASTY"]
    account_id: str

# POST /api/brokerage/sync
class SyncBrokerageRequest(BaseModel):
    account_id: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]

class SyncBrokerageResponse(BaseModel):
    trades_synced: int
    last_sync_date: datetime

# GET /api/brokerage/positions
class GetPositionsResponse(BaseModel):
    positions: List[Position]
```

Token management is automatic. Access and refresh tokens along with
`token_type`, expiration, and granted `scope` are stored for each brokerage
account. Tokens are refreshed when near expiry and the updated values are
persisted.

### 3.3 Trades
```python
# GET /api/trades
class GetTradesRequest(BaseModel):
    page: Optional[int] = 1
    limit: Optional[int] = 50
    symbol: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    tag_id: Optional[UUID]

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

Example usage:

`GET /api/trades?page=2&limit=5&symbol=AAPL&start_date=2024-01-01&end_date=2024-01-31`

```json
{
    "trades": [/* results page 2 of the filtered list */],
    "total": 12,
    "page": 2,
    "limit": 5
}
```

`GET /api/trades?tag_id=<uuid>` returns only trades associated with the provided `tag_id`.


### 3.4 Analytics
```python
# Query parameters shared by all analytics endpoints
class AnalyticsQueryParams(BaseModel):
    start_date: Optional[date]
    end_date: Optional[date]
    tag_id: Optional[UUID]

# GET /api/analytics/summary
# Example: GET /api/analytics/summary?start_date=2024-01-01&end_date=2024-03-31&tag_id=<UUID>
class AnalyticsSummary(BaseModel):
    total_trades: int
    win_rate: float
    average_win: Decimal
    average_loss: Decimal
    total_pnl: Decimal
    average_holding_time: timedelta

# GET /api/analytics/time-based
# Example: GET /api/analytics/time-based?start_date=2024-01-01&end_date=2024-03-31&tag_id=<UUID>
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
# Example: GET /api/analytics/tags?start_date=2024-01-01&end_date=2024-03-31
class TagAnalytics(BaseModel):
    tag_id: UUID
    tag_name: str
    trade_count: int
    win_rate: float
    total_pnl: Decimal

# GET /api/analytics/export
# Example: GET /api/analytics/export?start_date=2024-01-01&end_date=2024-03-31&tag_id=<UUID>
# Returns CSV or JSON based on Accept header
```

### 3.5 Journal Entries
```python
# GET /api/journal-entries
# Query Params:
#   ?start_date=ISO8601 datetime
#   &end_date=ISO8601 datetime
#   &trade_id=UUID
#   &tag_id=UUID
#   &search=string
#   &page=int
#   &limit=int

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
# Query Params:
#   ?query=string
#   &start_date=ISO8601 datetime
#   &end_date=ISO8601 datetime
```
### 3.6 Tags
Tags categorize trades and journal entries. Associations are stored in `trade_tags` and `journal_entry_tags` join tables.

```python
# GET /api/tags
class GetTagsResponse(BaseModel):
    tags: List[Tag]

# POST /api/tags
class CreateTagRequest(BaseModel):
    name: str

class TagResponse(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime

# PUT /api/tags/:id
class UpdateTagRequest(BaseModel):
    name: str

# DELETE /api/tags/:id
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
- Token refresh mechanism — brokerage access tokens are refreshed automatically
  using the stored refresh token and updated in the `brokerage_accounts` table
  when new tokens are issued
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

## 9. Trade Pipeline

### Overview
This section outlines how raw brokerage fills are transformed into trades.

### Entities
- **Fill**: A single execution from the brokerage API. Each fill records the symbol, side (buy/sell), quantity, price, timestamp and account.
- **Trade**: An aggregate of one or more fills. A trade moves through `OPEN`, `PARTIALLY_CLOSED` and `CLOSED` states.

### High Level Flow
1. Brokerage sync fetches fills from the external API.
2. Fills are stored verbatim in the `fills` table.
3. A background worker processes fills in time order per account and symbol.
4. Trades are created or updated based on the algorithm below.

### Trade Generation Algorithm
```python
for fill in fills_ordered_by_time(account, symbol):
    qty = fill.quantity if fill.side == "BUY" else -fill.quantity
    trade = find_latest_open_trade(account, symbol)

    if trade is None:
        trade = Trade(
            account_id=account,
            symbol=fill.symbol,
            direction="LONG" if qty > 0 else "SHORT",
            entry_date=fill.timestamp,
            entry_price=fill.price,
            open_qty=qty,
            state="OPEN",
        )
        save(trade)
    else:
        new_qty = trade.open_qty + qty
        if (trade.direction == "LONG" and qty > 0) or (trade.direction == "SHORT" and qty < 0):
            trade.entry_price = weighted_avg(trade.entry_price, trade.open_qty, fill.price, qty)
            trade.open_qty = new_qty
        else:
            trade.exit_price = weighted_avg(trade.exit_price, trade.closed_qty, fill.price, abs(qty))
            trade.closed_qty += abs(qty)
            trade.open_qty = max(0, trade.open_qty - abs(qty))

        if trade.open_qty == 0:
            trade.state = "CLOSED"
            trade.exit_date = fill.timestamp
        elif trade.closed_qty > 0:
            trade.state = "PARTIALLY_CLOSED"

        save(trade)

        if new_qty * trade.open_qty < 0:
            remaining_fill = qty + trade.open_qty
            create_trade_from_fill(remaining_fill, fill)
```

### Notes
- `open_qty` represents the current position size.
- `closed_qty` tracks how much of the position has been closed.
- When `open_qty` reaches zero the trade is `CLOSED`.
- If a closing fill is larger than the open quantity, the excess becomes a new trade in the fill's direction.

### Database Tables (simplified)
```sql
CREATE TABLE fills (
    id UUID PRIMARY KEY,
    account_id UUID NOT NULL,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL,   -- BUY or SELL
    quantity NUMERIC(10,2) NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE trades (
    id UUID PRIMARY KEY,
    account_id UUID NOT NULL,
    symbol TEXT NOT NULL,
    direction TEXT NOT NULL,       -- LONG or SHORT
    entry_date TIMESTAMP WITH TIME ZONE NOT NULL,
    exit_date TIMESTAMP WITH TIME ZONE,
    entry_price NUMERIC(10,2) NOT NULL,
    exit_price NUMERIC(10,2),
    open_qty NUMERIC(10,2) NOT NULL,
    closed_qty NUMERIC(10,2) NOT NULL DEFAULT 0,
    state TEXT NOT NULL,           -- OPEN, PARTIALLY_CLOSED, CLOSED
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```
