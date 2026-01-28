# Product Requirements & Backlog — Warehouse Scanner PWA MVP

## 1) Product overview
A single, installable PWA that scans a wide variety of barcodes via a webcam, then reliably places the decoded value on the clipboard for paste into spreadsheets. The MVP is optimized for fixed scanning stations but must be responsive and usable on phones/tablets. Offline reliability is mandatory.

## 2) Goals and non-goals
### Goals (MVP)
- Scan barcodes (1D + 2D) and copy the resulting text to the clipboard with minimal operator friction.
- Support a wide set of barcode formats (including checkout/retail codes, QR codes, and Data Matrix).
- Provide a clear UI/UX for scan state (ready, detected, copied, cooldown) to reduce operator errors.
- Work offline reliably (no CDN dependency; assets and scanning engine cached/packaged locally).
- Provide a responsive UI that works on fixed stations and mobile devices.

### Non-goals (MVP)
- Automated upload workflows (API upload or direct system integrations).
- Advanced analytics or multi-user account management.
- Regulatory compliance features (none required for now).

## 3) Key requirements
### Functional requirements
1. **Clipboard-first workflow**: After each successful scan, copy the decoded value to the clipboard. Offer a fallback copy action if permissions block auto-copy.
2. **Broad barcode support**: Support 1D and 2D formats commonly used in retail, logistics, and device identification, including:
   - Retail checkout barcodes (e.g., EAN/UPC)
   - QR codes (e.g., drone serial numbers)
   - Data Matrix (e.g., NZ Post tracking data)
3. **Multi-code handling**: If multiple codes appear in the frame, let the operator choose which one to copy.
4. **Scan state clarity**: Provide visible feedback for ready/detected/copy success/cooldown/error states.
5. **Fixed-station performance**: The default UX should be optimized for a fixed webcam station with minimal input overhead.
6. **Responsive layout**: UI adapts for phone/tablet use without breaking core scan flow.
7. **Offline-first**: The app must run without network connectivity. Scanner libraries and app assets must be available offline.

### Non-functional requirements
- **Reliability**: 100% offline availability for core scanning + copy flow.
- **Performance**: Minimal latency between detection and copy for throughput on the warehouse floor.
- **Usability**: Operators can complete scan → paste loops with minimal clicks/gestures.
- **Portability**: Single PWA usable across desktop, phone, and tablet.

## 4) MVP feature set
- **Camera control**: Start/stop camera, select camera device.
- **Live scan region** with status indicator.
- **Auto-copy to clipboard** (default) with fallback if blocked.
- **Optional “copy as row”** format (timestamp + semantic + type + value).
- **Multi-barcode selection modal**.
- **Recent scan log** (nice-to-have but useful for operator recovery; can be limited in MVP).
- **Offline packaging**: local scanner library + service worker asset caching.

## 5) User stories
1. **Warehouse operator (fixed station)**: “As an operator at a fixed station, I want to scan a barcode and immediately paste it into a spreadsheet without extra clicks, so I can process parcels quickly.”
2. **Operator handling multiple codes**: “As an operator, when multiple barcodes appear at once, I want to choose which code to copy so I don’t paste the wrong value.”
3. **Operator working offline**: “As an operator, I need the scanner to keep working when the network is down so I’m not blocked from processing parcels.”
4. **Mobile fallback use**: “As a field worker using a phone, I want the same PWA to work on mobile so I can scan and copy values anywhere.”
5. **Supervisor/reviewer**: “As a supervisor, I want a minimal scan log so I can verify recent scans if an operator reports a mismatch.”

## 6) Backlog (initial)
### Sprint 0 — Foundations
- [ ] Package the scanning library locally (remove CDN dependency).
- [ ] Add PWA manifest + service worker for offline asset caching.
- [ ] Define a canonical list of barcode formats to support.

### Sprint 1 — Core scanning + clipboard flow (MVP)
- [ ] Implement scanning pipeline using local assets.
- [ ] Start/stop camera + device selection.
- [ ] Clip-to-clipboard on successful scan.
- [ ] Multi-code selection modal.
- [ ] Ready/detected/cooldown UI states.
- [ ] Responsive UI adjustments for mobile screens.

### Sprint 2 — Usability enhancements
- [ ] Add optional copy-as-row toggle (timestamp + semantic + type + value).
- [ ] Add minimal recent scan log + copy-again action.
- [ ] Improve semantic labeling heuristics for common warehouse formats.

### Sprint 3 — Nice-to-haves
- [ ] CSV export of scan log.
- [ ] Optional upload mode (API integration) — post-MVP.

## 7) Open questions / decisions
- Confirm the exact list of barcode formats to guarantee support.
- Confirm the desired semantics labeling rules (GS1/SSCC/GTIN etc.).
- Decide the minimal UX for scan log in MVP (size, retention, export behavior).
