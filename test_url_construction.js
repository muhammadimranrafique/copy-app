// Test URL construction logic from mock-api.ts

function testUrlConstruction(params) {
  const qs = params && Object.keys(params).length ? `?${new URLSearchParams(params).toString()}` : '';
  const url = `/orders/${qs}`;
  console.log(`params: ${JSON.stringify(params)} => qs: "${qs}" => url: "${url}"`);
  return url;
}

// Test cases
console.log("Testing URL construction:");
testUrlConstruction(null);
testUrlConstruction({});
testUrlConstruction({ status: 'pending' });
testUrlConstruction({ status: 'pending', limit: 10 });