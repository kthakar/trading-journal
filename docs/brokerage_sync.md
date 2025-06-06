# Brokerage Sync Flow Specification

## Overview
The brokerage sync system will use OAuth2 for authentication and data access. Each brokerage has its own OAuth2 implementation and API endpoints. We'll create a unified interface to handle these differences.

## Supported Brokerages

### 1. Interactive Brokers (IBKR)
- **OAuth2 Flow**: Authorization Code with PKCE
- **API Base**: https://api.ibkr.com/v1
- **Scopes Required**:
  - `trades` - Read trade history
  - `positions` - Read current positions
  - `account` - Read account information
  - `market_data` - Read market data

### 2. Charles Schwab
- **OAuth2 Flow**: Authorization Code
- **API Base**: https://api.schwab.com/v1
- **Scopes Required**:
  - `trades.read` - Read trade history
  - `positions.read` - Read current positions
  - `account.read` - Read account information

### 3. Tastyworks
- **OAuth2 Flow**: Authorization Code
- **API Base**: https://api.tastyworks.com/v1
- **Scopes Required**:
  - `trades` - Read trade history
  - `positions` - Read current positions
  - `account` - Read account information

## Database Schema

```sql
-- Brokerage OAuth tokens
CREATE TABLE public.brokerage_oauth_tokens (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) NOT NULL,
    brokerage_type TEXT NOT NULL,
    account_id TEXT NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    token_type TEXT NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    scope TEXT[] NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    UNIQUE(user_id, brokerage_type, account_id)
);

-- Enable RLS
ALTER TABLE public.brokerage_oauth_tokens ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view own brokerage tokens" 
    ON public.brokerage_oauth_tokens FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own brokerage tokens" 
    ON public.brokerage_oauth_tokens FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own brokerage tokens" 
    ON public.brokerage_oauth_tokens FOR UPDATE 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own brokerage tokens" 
    ON public.brokerage_oauth_tokens FOR DELETE 
    USING (auth.uid() = user_id);
```

## API Endpoints

### 1. Initiate OAuth Flow
```python
# POST /api/brokerage/connect
class InitiateOAuthRequest(BaseModel):
    brokerage_type: Literal["IBKR", "SCHWAB", "TASTY"]
    account_id: str

class InitiateOAuthResponse(BaseModel):
    auth_url: str
    state: str
    code_verifier: str  # For IBKR PKCE flow
```

### 2. OAuth Callback
```python
# GET /api/brokerage/callback
class OAuthCallbackRequest(BaseModel):
    code: str
    state: str
    brokerage_type: Literal["IBKR", "SCHWAB", "TASTY"]
```

### 3. Sync Trades
```python
# POST /api/brokerage/sync
class SyncTradesRequest(BaseModel):
    brokerage_type: Literal["IBKR", "SCHWAB", "TASTY"]
    account_id: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]

class SyncTradesResponse(BaseModel):
    trades_synced: int
    last_sync_date: datetime
```

## Implementation Flow

### 1. Connect Brokerage Account
1. User clicks "Connect Brokerage" button
2. Frontend calls `/api/brokerage/connect` with brokerage type
3. Backend generates OAuth state and code verifier (for IBKR)
4. Backend returns auth URL and state
5. Frontend redirects user to brokerage OAuth page
6. User authorizes the application
7. Brokerage redirects back to our callback URL
8. Backend exchanges code for tokens
9. Backend stores tokens in database
10. Frontend shows success message

### 2. Sync Trades
1. User clicks "Sync Trades" button
2. Frontend calls `/api/brokerage/sync` with date range
3. Backend retrieves OAuth tokens from database
4. Backend checks if tokens need refresh
5. If needed, backend refreshes tokens
6. Backend calls brokerage API to fetch trades
7. Backend processes and stores trades
8. Backend returns sync results
9. Frontend updates UI with new trades

### 3. Token Refresh Flow
1. Backend checks token expiration before each API call
2. If token is expired or about to expire:
   - Backend calls brokerage refresh token endpoint
   - Backend updates stored tokens
   - Backend retries original API call
3. If refresh fails:
   - Backend marks connection as invalid
   - Frontend prompts user to reconnect

## Error Handling

### 1. OAuth Errors
- Invalid state parameter
- Authorization denied
- Invalid scope
- Network errors
- Rate limiting

### 2. API Errors
- Invalid tokens
- Rate limiting
- Network errors
- Data validation errors

### 3. Sync Errors
- Partial sync failures
- Duplicate trades
- Data inconsistencies
- Network timeouts

## Security Considerations

### 1. Token Storage
- Encrypt sensitive token data
- Use secure database connections
- Implement proper key rotation
- Regular token validation

### 2. API Security
- Validate all requests
- Implement rate limiting
- Use HTTPS for all communications
- Proper error handling

### 3. User Data Protection
- Implement RLS policies
- Regular security audits
- Proper logging
- Data encryption at rest

## Monitoring

### 1. Sync Status
- Track sync success/failure
- Monitor sync duration
- Track number of trades synced
- Monitor API rate limits

### 2. Error Tracking
- Log all errors
- Track error rates
- Monitor token refresh failures
- Track API response times

### 3. User Metrics
- Track connection success rate
- Monitor user engagement
- Track sync frequency
- Monitor data volume

## Frontend Components

### 1. Brokerage Connection
```typescript
// components/brokerage/BrokerageConnect.tsx
interface BrokerageConnectProps {
  brokerageType: 'IBKR' | 'SCHWAB' | 'TASTY';
  onSuccess: () => void;
  onError: (error: Error) => void;
}
```

### 2. Sync Status
```typescript
// components/brokerage/SyncStatus.tsx
interface SyncStatusProps {
  brokerageType: 'IBKR' | 'SCHWAB' | 'TASTY';
  accountId: string;
  lastSyncDate?: Date;
  onSync: () => Promise<void>;
}
```

### 3. Account List
```typescript
// components/brokerage/AccountList.tsx
interface AccountListProps {
  accounts: BrokerageAccount[];
  onDisconnect: (accountId: string) => Promise<void>;
  onSync: (accountId: string) => Promise<void>;
}
```

## Testing Strategy

### 1. Unit Tests
- OAuth flow validation
- Token refresh logic
- Data transformation
- Error handling

### 2. Integration Tests
- Complete OAuth flow
- Trade sync process
- Token refresh flow
- Error scenarios

### 3. E2E Tests
- Complete user journey
- Error recovery
- Rate limiting
- Network failures 