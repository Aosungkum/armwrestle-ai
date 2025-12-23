# Frontend Bug Fixes Log

This file tracks all bugs fixed in the frontend codebase.

## Date: 2025-01-27

### Issue #1: Token Storage Inconsistency
**Files Modified:** `script.js` (line 285)
- **Problem:** `script.js` was using `localStorage.getItem("token")` while `auth.js` uses `localStorage.getItem('auth_token')`
- **Fix:** Changed `fetchHistory()` function to use `localStorage.getItem("auth_token")` for consistency
- **Code Change:** Line 285: `const token = localStorage.getItem("token");` → `const token = localStorage.getItem("auth_token");`
- **Status:** ✅ Fixed

### Issue #2: Missing DOM Element Reference
**Files Modified:** `script.js` (line 328)
- **Problem:** `script.js` line 328 references `document.getElementById("historyBtn")` which doesn't exist in `index.html`, causing potential runtime error
- **Fix:** Added null check before attaching event listener: `const historyBtn = document.getElementById("historyBtn"); if (historyBtn) { ... }`
- **Code Change:** Wrapped event listener attachment in conditional check to prevent errors if element doesn't exist
- **Status:** ✅ Fixed

### Issue #3: Missing Authentication Header
**Files Modified:** `script.js` (lines 220-242)
- **Problem:** `analyzeVideo()` function doesn't include auth token in request headers, causing API to reject authenticated requests
- **Fix:** Added authentication header retrieval and inclusion in fetch request
- **Code Change:** Added token retrieval: `const token = localStorage.getItem('auth_token');` and header: `headers['Authorization'] = \`Bearer ${token}\`;`
- **Status:** ✅ Fixed

### Issue #4: API URL Inconsistency
**Files Modified:** `auth.js` (line 4)
- **Problem:** `auth.js` uses `'http://localhost:8000/api'` while `script.js` uses production URL `'https://armwrestle-ai-production.up.railway.app'`
- **Fix:** Updated `auth.js` constructor to use production URL: `this.API_URL = 'https://armwrestle-ai-production.up.railway.app/api';`
- **Code Change:** Changed API_URL from localhost to production URL for consistency
- **Status:** ✅ Fixed

### Issue #5: Unsafe JSON Parsing
**Files Modified:** `auth.js` (lines 5-12)
- **Problem:** `JSON.parse(localStorage.getItem('user') || 'null')` can throw error if localStorage has invalid JSON, crashing the app
- **Fix:** Wrapped JSON.parse in try-catch block with proper error handling
- **Code Change:** 
  ```javascript
  try {
      const userStr = localStorage.getItem('user');
      this.user = userStr ? JSON.parse(userStr) : null;
  } catch (error) {
      console.error('Error parsing user data from localStorage:', error);
      this.user = null;
  }
  ```
- **Status:** ✅ Fixed

### Issue #6: Missing Error Handling
**Files Modified:** `auth.js` (lines 93-120)
- **Problem:** `getStats()` and `getHistory()` don't check `response.ok` before parsing JSON, causing silent failures
- **Fix:** Added `response.ok` checks and proper error handling with meaningful error messages
- **Code Change:** 
  - Added `if (!response.ok)` checks before JSON parsing
  - Return proper error objects: `{ success: false, error: '...' }` instead of `null`
- **Status:** ✅ Fixed

### Issue #7: Incorrect Header Usage
**Files Modified:** `auth.js` (lines 86-90, 96, 111, 130)
- **Problem:** `headers: this.getAuthHeader()` passes object incorrectly - fetch API expects headers to be spread or properly formatted
- **Fix:** Changed all header usages to use spread operator: `headers: { ...this.getAuthHeader() }`
- **Code Change:** 
  - Updated `getStats()`, `getHistory()`, and `upgradePlan()` to use spread operator
  - Added null check in `getAuthHeader()` to return empty object if no token
- **Status:** ✅ Fixed

### Issue #8: Login Error Handling (Bonus Fix)
**Files Modified:** `auth.js` (lines 48-73)
- **Problem:** Login always returns generic 'Login failed' instead of using `data.error` from API response
- **Fix:** Added `response.ok` check and proper error extraction from API response
- **Code Change:** 
  ```javascript
  if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return { success: false, error: errorData.error || 'Login failed' };
  }
  // ... then use data.error in else block
  ```
- **Status:** ✅ Fixed

### Additional Fixes:
- **Null Safety:** Added null checks in `updateUIForAuthState()` to prevent errors if DOM elements don't exist
- **Error Handling:** Added error handling in `fetchHistory()` with try-catch and response.ok check
- **Error Messages:** Improved error messages in `analyzeVideo()` to show API error details when available

### Issue #9: Logout Crash/Redirect Issue
**Files Modified:** `auth.js` (lines 88-108), `index.html` (line 36), `dashboard.html` (line 33), `dashboard.js` (lines 11-20)
- **Problem:** Logout function was crashing or not redirecting properly:
  - Used `window.location.href = '/'` which might not resolve correctly
  - Didn't prevent default link behavior (`<a href="#">`)
  - Dashboard.js tried to access user properties without null checks
  - No error handling in logout function
- **Fix:** 
  - Updated logout to use proper redirect path (`index.html` or `./index.html`)
  - Added `event.preventDefault()` to logout links to prevent default navigation
  - Added try-catch error handling in logout function
  - Added UI update before redirect
  - Added null checks in dashboard.js for user data access
- **Code Changes:**
  ```javascript
  // auth.js - Improved logout
  logout() {
      try {
          this.token = null;
          this.user = null;
          localStorage.removeItem('auth_token');
          localStorage.removeItem('user');
          
          if (typeof updateUIForAuthState === 'function') {
              updateUIForAuthState();
          }
          
          const currentPath = window.location.pathname;
          const redirectPath = currentPath.includes('dashboard.html') ? 'index.html' : './index.html';
          window.location.href = redirectPath;
      } catch (error) {
          console.error('Logout error:', error);
          window.location.href = 'index.html';
      }
  }
  
  // HTML - Prevent default link behavior
  <a href="#" onclick="event.preventDefault(); auth.logout(); return false;">🚪 Logout</a>
  
  // dashboard.js - Added null checks
  if (user) {
      // Safe access to user properties
  }
  ```
- **Status:** ✅ Fixed

### Issue #10: Person Selection Not Working - Same Results for Both People
**Files Modified:** `backend/video_analyzer.py` (multiple functions), `frontend/script.js`, `frontend/auth.js`
- **Problem:** 
  - When selecting Person 1 (Left) or Person 2 (Right), the analysis results were identical
  - MediaPipe only detects one person per frame, so person matching was unreliable
  - Analysis always assumed right arm was active, not detecting which arm is actually being used
  - API URLs were changed to localhost, but user needs Railway URL for production
- **Fix:** 
  - **Reverted API URLs:** Changed back to Railway production URL (`https://armwrestle-ai-production.up.railway.app`)
  - **Improved Person Matching:** 
    - Collects all poses from video frames
    - Groups poses by position (left vs right) using midpoint threshold
    - Filters poses matching selected person's position
    - Falls back to position-based matching with lenient threshold if needed
  - **Active Arm Detection:** 
    - Automatically detects which arm is active (left or right) based on wrist position
    - Uses active arm for technique, risk, and strength analysis
    - Works for both left-handed and right-handed wrestlers
  - **Better Position Filtering:**
    - Uses detected people's positions to calculate midpoint
    - Matches poses based on left/right position relative to midpoint
    - Logs which person is being analyzed for debugging
- **Code Changes:**
  ```python
  # video_analyzer.py - Improved person matching
  # Collect all poses with positions
  all_poses = []
  for frame in video:
      if pose_detected:
          center_x = calculate_center(landmarks)
          all_poses.append({"landmarks": landmarks, "center_x": center_x})
  
  # Group by position (left vs right)
  if len(people_detected) > 1:
      midpoint = (left_person_x + right_person_x) / 2
  else:
      midpoint = 0.5
  
  # Filter for selected person
  for pose in all_poses:
      pose_position = "left" if pose["center_x"] < midpoint else "right"
      if pose_position == selected_person["position"]:
          person_landmarks.append(pose["landmarks"])
  
  # Active arm detection
  use_right_arm = right_wrist[1] < left_wrist[1]  # Higher on screen = active
  if use_right_arm:
      shoulder = right_shoulder
      elbow = right_elbow
      wrist = right_wrist
  else:
      shoulder = left_shoulder
      elbow = left_elbow
      wrist = left_wrist
  ```
- **Files Modified:**
  - `backend/video_analyzer.py`: 
    - `analyze_video()` - Improved person matching logic (lines ~430-543)
    - `detect_technique()` - Added active arm detection (lines ~52-110)
    - `assess_injury_risks()` - Uses active arm instead of assuming right (lines ~112-200)
    - `analyze_strength()` - Uses active arm instead of assuming right (lines ~200-280)
    - `analyze_person()` - Simplified to use single average landmarks (lines ~383-430)
  - `frontend/script.js`: Reverted API_URL to Railway production URL
  - `frontend/auth.js`: Reverted API_URL to Railway production URL
- **Status:** ✅ Fixed

