# MCP Chrome DevTools

Integration with Chrome DevTools for browser automation, performance analysis, and debugging.

## Capabilities

- **Performance Profiling**: Analyze runtime performance, memory usage, and CPU profiles
- **Network Monitoring**: Inspect network requests, responses, and timing
- **Console Access**: Capture console logs, errors, and warnings
- **DOM Inspection**: Query and manipulate the DOM
- **JavaScript Debugging**: Set breakpoints, step through code, inspect variables
- **Coverage Analysis**: Identify unused CSS and JavaScript

## Use Cases for AWS Monitoring Project

### 1. Frontend Performance Testing
- Profile dashboard loading times
- Analyze API request/response times
- Monitor memory leaks in monitoring dashboards
- Optimize bundle sizes and asset loading

### 2. API Testing
- Test API Gateway endpoints from browser context
- Verify CORS configurations
- Inspect authentication flows
- Debug WebSocket connections for real-time updates

### 3. Integration Testing
- Test web-based monitoring dashboards
- Verify event delivery and display
- Test notification rendering
- Validate responsive design

## Configuration

The Chrome DevTools MCP server enables:
- Automated browser testing
- Performance benchmarking
- Visual regression testing
- Accessibility auditing

## Example Usage

```javascript
// Profile API response time
const response = await fetch('/api/events');
console.time('parse-events');
const events = await response.json();
console.timeEnd('parse-events');

// Monitor memory usage
console.memory.usedJSHeapSize;

// Network timing
performance.getEntriesByType('navigation')[0];
```

## Integration Points

- Test frontend applications that consume monitoring APIs
- Validate real-time event displays
- Profile dashboard performance
- Debug authentication and authorization flows
