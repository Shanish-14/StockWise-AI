import React, { useState, useEffect, useMemo, useRef } from 'react';
import {
  LayoutDashboard,
  TrendingUp,
  Clock,
  Truck,
  ArrowLeftRight,
  Sliders,
  Search,
  Bell,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Package,
  Store,
  Calendar,
  RefreshCw,
  Upload,
  ScanLine,
  Trash2,
  Plus,
  ArrowRight,
  ShieldAlert,
  BarChart3,
  Activity,
  ChevronRight,
  Menu,
  X,
  Info,
  Zap,
  Layers,
  MapPin
} from 'lucide-react';

// ============================================================================
// HIGH-RESOLUTION SUPERMARKET PHOTOGRAPHY ASSETS (VERIFIED UNSPLASH URLS)
// ============================================================================
const PAGE_BACKGROUNDS = {
  overview: {
    url: 'https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=1920&q=85',
    fallback: 'linear-gradient(135deg, #060d1a 0%, #0d2b24 50%, #061326 100%)',
    caption: 'Flagship Supermarket Main Aisle'
  },
  forecasting: {
    url: 'https://images.unsplash.com/photo-1578916171728-46686eac8d58?auto=format&fit=crop&w=1920&q=85',
    fallback: 'linear-gradient(135deg, #071422 0%, #0f3628 50%, #060d1a 100%)',
    caption: 'Fresh Produce & Harvest Display'
  },
  expiry: {
    url: 'https://images.unsplash.com/photo-1604719312566-8912e9227c6a?auto=format&fit=crop&w=1920&q=85',
    fallback: 'linear-gradient(135deg, #060d1a 0%, #12332a 50%, #0a192f 100%)',
    caption: 'Refrigerated Dairy & Organic Section'
  },
  supplier: {
    url: 'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=1920&q=85',
    fallback: 'linear-gradient(135deg, #060d1a 0%, #13253a 50%, #091c24 100%)',
    caption: 'Regional Cold-Chain Distribution Hub'
  },
  transfer: {
    url: 'https://images.unsplash.com/photo-1534723452862-4c874018d66d?auto=format&fit=crop&w=1920&q=85',
    fallback: 'linear-gradient(135deg, #071221 0%, #0e3026 50%, #060d1a 100%)',
    caption: 'Multi-Store Retail Floor & Carts'
  },
  whatif: {
    url: 'https://images.unsplash.com/photo-1506617420156-8e4536971650?auto=format&fit=crop&w=1920&q=85',
    fallback: 'linear-gradient(135deg, #081224 0%, #143629 50%, #060d1a 100%)',
    caption: 'Artisanal Bakery & Gourmet Gallery'
  }
};

// ============================================================================
// SAMPLE DEMONSTRATION DATASETS
// ============================================================================
const STORES = [
  { id: 'ST-01', name: 'Downtown Flagship #01', district: 'Central Metro', health: 94, skus: 4210, surplus: 310, shortage: 45 },
  { id: 'ST-02', name: 'Westside Market #02', district: 'West Bay', health: 86, skus: 3680, surplus: 120, shortage: 185 },
  { id: 'ST-03', name: 'Harborview Plaza #03', district: 'Marina District', health: 91, skus: 3540, surplus: 245, shortage: 70 },
  { id: 'ST-04', name: 'Northgate Store #04', district: 'North Hills', health: 82, skus: 3390, surplus: 95, shortage: 220 }
];

const PRODUCTS = [
  { id: 'PRD-101', name: 'Organic Hass Avocados (4-Pack)', category: 'Fresh Produce', baseDemand: 320, unitPrice: 5.99, safetyBuffer: 85 },
  { id: 'PRD-102', name: 'Farmstead Whole Milk 1L', category: 'Dairy & Chilled', baseDemand: 540, unitPrice: 3.49, safetyBuffer: 140 },
  { id: 'PRD-103', name: 'Sourdough Artisanal Loaf', category: 'In-Store Bakery', baseDemand: 210, unitPrice: 6.25, safetyBuffer: 50 },
  { id: 'PRD-104', name: 'Fresh Atlantic Salmon Fillet', category: 'Seafood Counter', baseDemand: 145, unitPrice: 14.99, safetyBuffer: 35 },
  { id: 'PRD-105', name: 'Cold-Pressed Extra Virgin Olive Oil', category: 'Pantry & Gourmet', baseDemand: 180, unitPrice: 16.50, safetyBuffer: 60 }
];

const INITIAL_EXPIRY_ITEMS = [
  { id: 'EXP-901', sku: 'DRY-204', name: 'Organic Greek Yogurt 500g', category: 'Dairy & Chilled', batch: 'BCH-8841', qty: 48, expiryDate: '2026-11-24', store: 'Downtown Flagship #01' },
  { id: 'EXP-902', sku: 'PRD-104', name: 'Fresh Atlantic Salmon Fillet', category: 'Seafood Counter', batch: 'BCH-8902', qty: 26, expiryDate: '2026-11-28', store: 'Harborview Plaza #03' },
  { id: 'EXP-903', sku: 'BKR-312', name: 'Sourdough Artisanal Loaf', category: 'In-Store Bakery', batch: 'BCH-8919', qty: 34, expiryDate: '2026-11-29', store: 'Westside Market #02' },
  { id: 'EXP-904', sku: 'PRD-101', name: 'Organic Hass Avocados (4-Pack)', category: 'Fresh Produce', batch: 'BCH-8955', qty: 112, expiryDate: '2026-12-06', store: 'Downtown Flagship #01' },
  { id: 'EXP-905', sku: 'DRY-118', name: 'Farmstead Whole Milk 1L', category: 'Dairy & Chilled', batch: 'BCH-8970', qty: 195, expiryDate: '2026-12-12', store: 'Northgate Store #04' },
  { id: 'EXP-906', sku: 'PNT-409', name: 'Cold-Pressed Olive Oil 750ml', category: 'Pantry & Gourmet', batch: 'BCH-8710', qty: 84, expiryDate: '2027-04-18', store: 'Downtown Flagship #01' }
];

const OCR_SCAN_PRESETS = [
  {
    id: 'preset-dairy',
    label: 'Dairy Carton Label',
    badge: 'Chilled Dairy',
    extracted: {
      sku: 'DRY-512',
      name: 'Organic Meadow Butter 250g',
      category: 'Dairy & Chilled',
      batch: 'BCH-9044',
      qty: '64',
      expiryDate: '2026-11-30',
      store: 'Downtown Flagship #01'
    },
    confidence: '99.2%'
  },
  {
    id: 'preset-produce',
    label: 'Produce Crate Barcode',
    badge: 'Fresh Harvest',
    extracted: {
      sku: 'PRD-219',
      name: 'Hydroponic Baby Spinach 300g',
      category: 'Fresh Produce',
      batch: 'BCH-9081',
      qty: '90',
      expiryDate: '2026-11-28',
      store: 'Westside Market #02'
    },
    confidence: '98.7%'
  },
  {
    id: 'preset-bakery',
    label: 'Bakery Batch Sticker',
    badge: 'Artisan Bakery',
    extracted: {
      sku: 'BKR-405',
      name: 'Brioche Burger Buns (6-Pack)',
      category: 'In-Store Bakery',
      batch: 'BCH-9103',
      qty: '52',
      expiryDate: '2026-12-03',
      store: 'Harborview Plaza #03'
    },
    confidence: '97.9%'
  }
];

const SUPPLIERS = [
  { id: 'SUP-01', name: 'FreshDirect Valley Farms', specialty: 'Produce & Organics', defaultReliability: 94, avgDistance: 85 },
  { id: 'SUP-02', name: 'Nordic Creamery & Dairy Co.', specialty: 'Chilled Dairy', defaultReliability: 91, avgDistance: 140 },
  { id: 'SUP-03', name: 'Pacific Cold-Chain Seafoods', specialty: 'Fresh Seafood', defaultReliability: 82, avgDistance: 310 },
  { id: 'SUP-04', name: 'Metro Gourmet Dry Goods', specialty: 'Pantry & Imports', defaultReliability: 96, avgDistance: 210 }
];

const INITIAL_TRANSFERS = [
  {
    id: 'TRF-401',
    product: 'Organic Hass Avocados (4-Pack)',
    sku: 'PRD-101',
    donor: 'Downtown Flagship #01',
    receiver: 'Westside Market #02',
    donorSurplus: 145,
    receiverShortage: 92,
    recommendedQty: 90,
    distanceKm: 11.4,
    urgency: 'High',
    status: 'Recommended'
  },
  {
    id: 'TRF-402',
    product: 'Farmstead Whole Milk 1L',
    sku: 'PRD-102',
    donor: 'Harborview Plaza #03',
    receiver: 'Northgate Store #04',
    donorSurplus: 180,
    receiverShortage: 130,
    recommendedQty: 120,
    distanceKm: 16.8,
    urgency: 'High',
    status: 'Recommended'
  },
  {
    id: 'TRF-403',
    product: 'Sourdough Artisanal Loaf',
    sku: 'PRD-103',
    donor: 'Downtown Flagship #01',
    receiver: 'Northgate Store #04',
    donorSurplus: 65,
    receiverShortage: 48,
    recommendedQty: 45,
    distanceKm: 19.2,
    urgency: 'Medium',
    status: 'Recommended'
  },
  {
    id: 'TRF-404',
    product: 'Fresh Atlantic Salmon Fillet',
    sku: 'PRD-104',
    donor: 'Harborview Plaza #03',
    receiver: 'Westside Market #02',
    donorSurplus: 42,
    receiverShortage: 30,
    recommendedQty: 28,
    distanceKm: 9.6,
    urgency: 'Medium',
    status: 'Recommended'
  }
];

const RECENT_ACTIVITIES = [
  { id: 1, title: 'Demand Surge Detected: Fresh Produce', detail: '+18.4% weekend uplift predicted at Downtown Flagship #01', time: '6 mins ago', type: 'forecast' },
  { id: 2, title: 'Expiry Alert Triggered (26 Units)', detail: 'Fresh Atlantic Salmon Fillet expires within 48 hours at Harborview #03', time: '19 mins ago', type: 'expiry' },
  { id: 3, title: 'Inter-Store Transfer Optimized', detail: 'Route ST-01 → ST-02 saves $640 in potential spoilage', time: '42 mins ago', type: 'transfer' },
  { id: 4, title: 'Supplier Route Weather Advisory', detail: 'Pacific Cold-Chain Seafoods transit risk elevated to 44%', time: '1 hr ago', type: 'supplier' }
];

// ============================================================================
// CUSTOM STOCKWISE AI LOGO COMPONENT
// ============================================================================
const StockWiseLogo = ({ size = 'md' }) => {
  const dim = size === 'lg' ? 44 : 36;
  return (
    <div className="flex items-center gap-3 select-none">
      <div
        className="relative flex items-center justify-center rounded-xl bg-gradient-to-br from-emerald-400 via-emerald-500 to-teal-700 shadow-lg shadow-emerald-500/30 border border-emerald-300/40"
        style={{ width: dim, height: dim }}
      >
        <svg width={dim * 0.62} height={dim * 0.62} viewBox="0 0 24 24" fill="none">
          <path
            d="M3 7L12 2L21 7V17L12 22L3 17V7Z"
            stroke="#041019"
            strokeWidth="2.2"
            strokeLinejoin="round"
          />
          <path
            d="M7.5 13.5L10.5 10.5L13 13L16.8 8.8"
            stroke="#ffffff"
            strokeWidth="2.3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <circle cx="16.8" cy="8.8" r="1.6" fill="#ffffff" />
        </svg>
      </div>
      <div>
        <div className="flex items-center gap-1.5">
          <span className={`font-bold tracking-tight text-white ${size === 'lg' ? 'text-2xl' : 'text-lg'}`}>
            StockWise
          </span>
          <span className="px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wider rounded bg-emerald-500/25 text-emerald-300 border border-emerald-400/40">
            AI
          </span>
        </div>
        {size === 'lg' && (
          <p className="text-xs text-emerald-300/90 font-medium tracking-wide">
            Enterprise Retail Intelligence
          </p>
        )}
      </div>
    </div>
  );
};

// ============================================================================
// INTERACTIVE SVG LINE / AREA CHART COMPONENT
// ============================================================================
const InteractiveDemandChart = ({ data, height = 250 }) => {
  const [hoverIdx, setHoverIdx] = useState(null);
  const width = 680;
  const padLeft = 46;
  const padRight = 22;
  const padTop = 24;
  const padBottom = 34;

  const maxVal = useMemo(() => {
    const allVals = data.flatMap((d) => [d.actual || 0, d.predicted || 0, d.upper || 0]);
    return Math.ceil((Math.max(...allVals, 100) * 1.12) / 50) * 50;
  }, [data]);

  const plotW = width - padLeft - padRight;
  const plotH = height - padTop - padBottom;

  const getX = (index) => padLeft + (index / Math.max(data.length - 1, 1)) * plotW;
  const getY = (val) => padTop + plotH - (val / maxVal) * plotH;

  const predictedPoints = data.map((d, i) => `${getX(i)},${getY(d.predicted)}`).join(' ');
  const actualData = data.filter((d) => d.actual !== null && d.actual !== undefined);
  const actualPoints = actualData
    .map((d, i) => {
      const origIdx = data.findIndex((item) => item.label === d.label);
      return `${getX(origIdx)},${getY(d.actual)}`;
    })
    .join(' ');

  const areaPath = useMemo(() => {
    if (!data.length) return '';
    const topPts = data.map((d, i) => `${getX(i)},${getY(d.predicted)}`).join(' L ');
    return `M ${getX(0)},${padTop + plotH} L ${topPts} L ${getX(data.length - 1)},${padTop + plotH} Z`;
  }, [data, maxVal]);

  const confidenceBandPath = useMemo(() => {
    if (!data.length || data[0].upper === undefined) return '';
    const upperPts = data.map((d, i) => `${getX(i)},${getY(d.upper)}`).join(' L ');
    const lowerPts = [...data]
      .reverse()
      .map((d, revI) => {
        const origI = data.length - 1 - revI;
        return `${getX(origI)},${getY(d.lower)}`;
      })
      .join(' L ');
    return `M ${upperPts} L ${lowerPts} Z`;
  }, [data, maxVal]);

  const yTicks = [0, 0.25, 0.5, 0.75, 1].map((t) => Math.round(t * maxVal));

  return (
    <div className="relative w-full select-none">
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto overflow-visible">
        <defs>
          <linearGradient id="emeraldAreaGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#10b981" stopOpacity="0.38" />
            <stop offset="100%" stopColor="#10b981" stopOpacity="0.0" />
          </linearGradient>
        </defs>

        {/* Horizontal Grid Lines */}
        {yTicks.map((tick, i) => {
          const y = getY(tick);
          return (
            <g key={i}>
              <line
                x1={padLeft}
                y1={y}
                x2={width - padRight}
                y2={y}
                stroke="rgba(255,255,255,0.09)"
                strokeDasharray="4 4"
              />
              <text
                x={padLeft - 8}
                y={y + 4}
                textAnchor="end"
                fill="rgba(203,213,225,0.75)"
                fontSize="11"
                fontFamily="monospace"
              >
                {tick}
              </text>
            </g>
          );
        })}

        {/* Confidence Band if available */}
        {confidenceBandPath && (
          <path d={confidenceBandPath} fill="rgba(52, 211, 153, 0.14)" />
        )}

        {/* Predicted Area Fill */}
        <path d={areaPath} fill="url(#emeraldAreaGrad)" />

        {/* Predicted Line */}
        <polyline
          fill="none"
          stroke="#10b981"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
          points={predictedPoints}
        />

        {/* Actual Line */}
        {actualPoints && (
          <polyline
            fill="none"
            stroke="#38bdf8"
            strokeWidth="2.5"
            strokeDasharray="5 4"
            strokeLinecap="round"
            strokeLinejoin="round"
            points={actualPoints}
          />
        )}

        {/* Data Points & Hover Targets */}
        {data.map((d, i) => {
          const cx = getX(i);
          const cyPred = getY(d.predicted);
          const isHovered = hoverIdx === i;

          return (
            <g key={i}>
              {isHovered && (
                <line
                  x1={cx}
                  y1={padTop}
                  x2={cx}
                  y2={padTop + plotH}
                  stroke="rgba(52, 211, 153, 0.5)"
                  strokeWidth="1.5"
                />
              )}

              {d.actual !== null && d.actual !== undefined && (
                <circle
                  cx={cx}
                  cy={getY(d.actual)}
                  r={isHovered ? 5.5 : 3.5}
                  fill="#38bdf8"
                  stroke="#060d1a"
                  strokeWidth="1.5"
                />
              )}

              <circle
                cx={cx}
                cy={cyPred}
                r={isHovered ? 6.5 : 4}
                fill="#10b981"
                stroke="#ffffff"
                strokeWidth={isHovered ? 2 : 1.5}
              />

              <text
                x={cx}
                y={height - 10}
                textAnchor="middle"
                fill={isHovered ? '#34d399' : 'rgba(203,213,225,0.75)'}
                fontSize="11"
                fontWeight={isHovered ? '700' : '400'}
              >
                {d.label}
              </text>

              {/* Invisible wide column for smooth hover */}
              <rect
                x={cx - plotW / data.length / 2}
                y={padTop}
                width={plotW / data.length}
                height={plotH}
                fill="transparent"
                className="cursor-pointer"
                onMouseEnter={() => setHoverIdx(i)}
                onMouseLeave={() => setHoverIdx(null)}
              />
            </g>
          );
        })}
      </svg>

      {/* Interactive Floating Tooltip */}
      {hoverIdx !== null && data[hoverIdx] && (
        <div
          className="pointer-events-none absolute top-2 right-3 z-20 rounded-xl bg-slate-950/90 border border-emerald-400/40 px-3.5 py-2.5 shadow-xl backdrop-blur-md text-xs"
        >
          <div className="font-semibold text-white mb-1">{data[hoverIdx].label}</div>
          <div className="flex items-center gap-2 text-emerald-300">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            <span>AI Forecast: <strong>{data[hoverIdx].predicted} units</strong></span>
          </div>
          {data[hoverIdx].actual !== null && data[hoverIdx].actual !== undefined && (
            <div className="flex items-center gap-2 text-sky-300 mt-0.5">
              <span className="w-2 h-2 rounded-full bg-sky-400" />
              <span>Actual Sales: <strong>{data[hoverIdx].actual} units</strong></span>
            </div>
          )}
          {data[hoverIdx].upper !== undefined && (
            <div className="text-[11px] text-slate-400 mt-1">
              95% CI: {data[hoverIdx].lower} – {data[hoverIdx].upper} units
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// ============================================================================
// MAIN APPLICATION COMPONENT
// ============================================================================
export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [globalSearch, setGlobalSearch] = useState('');
  const [selectedStoreGlobal, setSelectedStoreGlobal] = useState('ALL');
  const [toastMessage, setToastMessage] = useState(null);

  // Preload all 6 supermarket background images on initial mount
    Object.values(PAGE_BACKGROUNDS).forEach((bg) => {
      const img = new Image();
      img.src = bg.url;
    });
  }, []);

  const showToast = (title, detail) => {
    setToastMessage({ title, detail });
    setTimeout(() => {
      setToastMessage((prev) => (prev?.title === title ? null : prev));
    }, 3800);
  };useEffect(() => {
  const fetchExpiryProducts = async () => {
    try {
      setIsLoadingExpiry(true);

      const response = await fetch('http://127.0.0.1:8000/api/expiry/');

      if (!response.ok) {
        throw new Error('Failed to fetch expiry products');
      }

      const data = await response.json();

      const formattedProducts = data.products.map((product) => ({
        id: product.id,
        sku: product.sku || '',
        name: product.product_name,
        category: product.category || 'Other',
        batch: product.batch_number,
        qty: product.quantity,
        expiryDate: product.expiry_date,
        store: product.store || 'Downtown Flagship #01'
      }));

      setExpiryItems(formattedProducts);
    } catch (error) {
      console.error('Expiry loading error:', error);
      showToast('Loading Failed', 'Could not load expiry products from the backend.');
    } finally {
      setIsLoadingExpiry(false);
    }
  };

  fetchExpiryProducts();
}, []);
  

  // Navigation items in EXACT required order
  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard, badge: null },
    { id: 'forecasting', label: 'Demand Forecasting', icon: TrendingUp, badge: 'AI' },
    { id: 'expiry', label: 'Expiry Management', icon: Clock, badge: 'OCR' },
    { id: 'supplier', label: 'Supplier Delay Prediction', icon: Truck, badge: 'Beta' },
    { id: 'transfer', label: 'Inter-Store Stock Transfer', icon: ArrowLeftRight, badge: '4' },
    { id: 'whatif', label: 'What-if Analysis', icon: Sliders, badge: null }
  ];

  // --------------------------------------------------------------------------
  // FEATURE 1 STATE: DEMAND FORECASTING
  // --------------------------------------------------------------------------
  const [fcProduct, setFcProduct] = useState(PRODUCTS[0].id);
  const [fcStore, setFcStore] = useState(STORES[0].id);
  const [fcDate, setFcDate] = useState('2026-12-03');
  const [fcHorizon, setFcHorizon] = useState('7');
  const [fcLoading, setFcLoading] = useState(false);
  const [fcSeed, setFcSeed] = useState(1);

  const handleGenerateForecast = () => {
    setFcLoading(true);
    setTimeout(() => {
      setFcSeed((s) => s + 1);
      setFcLoading(false);
      const prod = PRODUCTS.find((p) => p.id === fcProduct);
      showToast('Demand Forecast Updated', `Generated ${fcHorizon}-day projection for ${prod?.name}`);
    }, 450);
  };

  const forecastSeries = useMemo(() => {
    const prod = PRODUCTS.find((p) => p.id === fcProduct) || PRODUCTS[0];
    const storeIndex = STORES.findIndex((s) => s.id === fcStore);
    const storeFactor = [1.18, 0.94, 1.05, 0.88][storeIndex] || 1.0;
    const days = parseInt(fcHorizon, 10) || 7;
    const dayNames = ['Thu', 'Fri', 'Sat', 'Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun', 'Mon', 'Tue', 'Wed'];

    return Array.from({ length: days }).map((_, idx) => {
      const weekendBoost = idx % 7 === 2 || idx % 7 === 3 ? 1.24 : 1.0;
      const wave = Math.sin((idx + fcSeed) * 0.85) * 0.09;
      const predicted = Math.round(prod.baseDemand * storeFactor * weekendBoost * (1 + wave));
      const hasActual = idx < Math.ceil(days * 0.55);
      const actual = hasActual ? Math.round(predicted * (0.95 + ((idx * 7) % 10) * 0.011)) : null;
      const margin = Math.round(predicted * 0.08);
      return {
        label: `${dayNames[idx % dayNames.length]} +${idx + 1}d`,
        predicted,
        actual,
        lower: predicted - margin,
        upper: predicted + margin
      };
    });
  }, [fcProduct, fcStore, fcHorizon, fcSeed]);

  // --------------------------------------------------------------------------
  // FEATURE 2 STATE: EXPIRY MANAGEMENT & OCR SCANNER
  // --------------------------------------------------------------------------
  
  const [expiryItems, setExpiryItems] = useState([]);
  const [isLoadingExpiry, setIsLoadingExpiry] = useState(true);
  const [expiryFilter, setExpiryFilter] = useState('ALL');
  const [isScanningOcr, setIsScanningOcr] = useState(false);
  const [ocrResultBanner, setOcrResultBanner] = useState(null);
  const [uploadedPreviewName, setUploadedPreviewName] = useState('');
  const [newProductForm, setNewProductForm] = useState({
    sku: '',
    name: '',
    category: 'Dairy & Chilled',
    batch: '',
    qty: '',
    expiryDate: '2026-12-01',
    store: 'Downtown Flagship #01'
  });
  const [formError, setFormError] = useState('');

  const referenceToday = new Date('2026-11-26T00:00:00');

  const getExpiryStatus = (dateStr) => {
    const target = new Date(`${dateStr}T00:00:00`);
    const diffDays = Math.ceil((target - referenceToday) / (1000 * 60 * 60 * 24));
    if (diffDays < 0) return { code: 'EXPIRED', label: `Expired (${Math.abs(diffDays)}d ago)`, days: diffDays };
    if (diffDays <= 5) return { code: 'SOON', label: `Expiring in ${diffDays}d`, days: diffDays };
    return { code: 'SAFE', label: `Safe (${diffDays}d left)`, days: diffDays };
  };

  const triggerOcrScan = (preset, fileName = '') => {
    setIsScanningOcr(true);
    setOcrResultBanner(null);
    setUploadedPreviewName(fileName || preset.label);
    setTimeout(() => {
      setIsScanningOcr(false);
      setNewProductForm(preset.extracted);
      setOcrResultBanner({
        confidence: preset.confidence,
        text: `Extracted SKU ${preset.extracted.sku} • Batch ${preset.extracted.batch} • Exp ${preset.extracted.expiryDate}`
      });
      showToast('OCR Label Scan Complete', `Auto-filled ${preset.extracted.name} (${preset.confidence} confidence)`);
    }, 900);
  };

  const handleFileUploadOcr = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const randomPreset = OCR_SCAN_PRESETS[Math.floor(Math.random() * OCR_SCAN_PRESETS.length)];
    triggerOcrScan(randomPreset, file.name);
  };

  
const handleAddExpiryProduct = async (e) => {
  e.preventDefault();

  if (
    !newProductForm.name.trim() ||
    !newProductForm.sku.trim() ||
    !newProductForm.qty ||
    !newProductForm.expiryDate
  ) {
    setFormError('Please fill in SKU, Product Name, Quantity, and Expiry Date.');
    return;
  }

  setFormError('');

  const productData = {
    sku: newProductForm.sku.trim().toUpperCase(),
    product_name: newProductForm.name.trim(),
    category: newProductForm.category,
    batch_number: newProductForm.batch.trim() || `BCH-${Math.floor(1000 + Math.random() * 9000)}`,
    quantity: parseInt(newProductForm.qty, 10),
    expiry_date: newProductForm.expiryDate,
    store: newProductForm.store
  };

  try {
    // Save product to the SQLite database through FastAPI
    const response = await fetch('http://127.0.0.1:8000/api/expiry/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(productData)
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.detail || 'Failed to add product.');
    }

    // Fetch the updated product list from the database
    const listResponse = await fetch('http://127.0.0.1:8000/api/expiry/');

    if (!listResponse.ok) {
      throw new Error('Product saved, but refreshing the list failed.');
    }

    const data = await listResponse.json();

    const formattedProducts = data.products.map((product) => ({
      id: product.id,
      sku: product.sku || '',
      name: product.product_name,
      category: product.category || 'Other',
      batch: product.batch_number,
      qty: product.quantity,
      expiryDate: product.expiry_date,
      store: product.store || 'Downtown Flagship #01'
    }));

    setExpiryItems(formattedProducts);

    setNewProductForm({
      sku: '',
      name: '',
      category: 'Dairy & Chilled',
      batch: '',
      qty: '',
      expiryDate: '2026-12-01',
      store: 'Downtown Flagship #01'
    });

    setOcrResultBanner(null);

    showToast(
      'Batch Registered',
      `${productData.product_name} saved successfully to the database.`
    );

  } catch (error) {
    console.error('Add product error:', error);
    setFormError(error.message || 'Could not save product. Please try again.');
  }
};


const handleDeleteExpiryProduct = async (id) => {
  try {
    const response = await fetch(
      `http://127.0.0.1:8000/api/expiry/${id}`,
      {
        method: 'DELETE'
      }
    );

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.detail || 'Failed to delete product.');
    }

    setExpiryItems((prev) =>
      prev.filter((item) => item.id !== id)
    );

    showToast(
      'Product Removed',
      'Inventory batch removed from the database.'
    );

  } catch (error) {
    console.error('Delete product error:', error);
    showToast('Delete Failed', error.message);
  }
};


  const handleDeleteExpiryProduct = (id) => {
    setExpiryItems((prev) => prev.filter((item) => item.id !== id));
    showToast('Product Removed', 'Inventory batch removed from tracking table.');
  };

  // --------------------------------------------------------------------------
  // FEATURE 3 STATE: SUPPLIER DELAY PREDICTION
  // --------------------------------------------------------------------------
  const [supId, setSupId] = useState(SUPPLIERS[2].id);
  const [supStore, setSupStore] = useState(STORES[0].id);
  const [supProduct, setSupProduct] = useState(PRODUCTS[3].id);
  const [supQty, setSupQty] = useState(420);
  const [supDistance, setSupDistance] = useState(310);
  const [supReliability, setSupReliability] = useState(82);
  const [supCapacity, setSupCapacity] = useState(86);
  const [delayResult, setDelayResult] = useState({
    probability: 64,
    riskLevel: 'High',
    estDelayHours: 5.5,
    factors: [
      { label: 'Carrier Capacity Strain', score: 74 },
      { label: 'Long-Haul Cold Transit Distance', score: 68 },
      { label: 'Historical On-Time Variance', score: 52 }
    ]
  });

  const handleSupplierChange = (newSupId) => {
    setSupId(newSupId);
    const found = SUPPLIERS.find((s) => s.id === newSupId);
    if (found) {
      setSupReliability(found.defaultReliability);
      setSupDistance(found.avgDistance);
    }
  };

  const handlePredictDelay = () => {
    const relRisk = (100 - supReliability) * 1.45;
    const distRisk = Math.min(35, (supDistance / 600) * 35);
    const capRisk = Math.max(0, (supCapacity - 65) * 0.95);
    const qtyRisk = Math.min(18, (supQty / 1200) * 18);

    const rawProb = Math.min(96, Math.max(6, Math.round(relRisk + distRisk + capRisk + qtyRisk)));
    const riskLevel = rawProb >= 60 ? 'High' : rawProb >= 32 ? 'Moderate' : 'Low';
    const estDelayHours = Number(((rawProb / 100) * 8.5).toFixed(1));

    setDelayResult({
      probability: rawProb,
      riskLevel,
      estDelayHours,
      factors: [
        { label: 'Carrier Capacity Utilization', score: Math.min(98, Math.round(supCapacity * 0.92)) },
        { label: 'Route Distance & Cold-Chain Exposure', score: Math.min(95, Math.round((supDistance / 500) * 100)) },
        { label: 'Supplier Reliability Deficit', score: Math.min(95, Math.round((100 - supReliability) * 2.4)) }
      ]
    });
    showToast('Delay Risk Calculated', `Predicted ${rawProb}% delay probability (${riskLevel} Risk)`);
  };

  // --------------------------------------------------------------------------
  // FEATURE 4 STATE: INTER-STORE STOCK TRANSFER
  // --------------------------------------------------------------------------
  const [donorStoreId, setDonorStoreId] = useState('ST-01');
  const [receiverStoreId, setReceiverStoreId] = useState('ST-02');
  const [transfers, setTransfers] = useState(INITIAL_TRANSFERS);

  const handleApproveTransfer = (id) => {
    setTransfers((prev) =>
      prev.map((trf) => (trf.id === id ? { ...trf, status: 'Dispatched' } : trf))
    );
    showToast('Transfer Dispatched', `Fleet manifest ${id} scheduled for inter-store rebalancing.`);
  };

  const handleCreateCustomTransfer = () => {
    if (donorStoreId === receiverStoreId) {
      showToast('Invalid Route', 'Donor and Receiver stores must be different locations.');
      return;
    }
    const donorObj = STORES.find((s) => s.id === donorStoreId);
    const receiverObj = STORES.find((s) => s.id === receiverStoreId);
    const newTrf = {
      id: `TRF-${Math.floor(500 + Math.random() * 400)}`,
      product: 'Cold-Pressed Extra Virgin Olive Oil',
      sku: 'PRD-105',
      donor: donorObj.name,
      receiver: receiverObj.name,
      donorSurplus: 88,
      receiverShortage: 60,
      recommendedQty: 55,
      distanceKm: 14.2,
      urgency: 'Medium',
      status: 'Recommended'
    };
    setTransfers((prev) => [newTrf, ...prev]);
    showToast('Transfer Route Generated', `Balanced surplus from ${donorObj.name} to ${receiverObj.name}`);
  };

  // --------------------------------------------------------------------------
  // FEATURE 5 STATE: WHAT-IF ANALYSIS
  // --------------------------------------------------------------------------
  const [demandDeltaPct, setDemandDeltaPct] = useState(20);
  const [targetCoverageDays, setTargetCoverageDays] = useState(12);
  const [leadTimeBufferDays, setLeadTimeBufferDays] = useState(3);

  const whatIfMetrics = useMemo(() => {
    const baselineDailyDemand = 1395; // sum across core SKUs
    const currentOnHand = 15200;
    const simulatedDailyDemand = Math.round(baselineDailyDemand * (1 + demandDeltaPct / 100));
    const requiredStock = simulatedDailyDemand * (targetCoverageDays + leadTimeBufferDays);
    const netBalance = currentOnHand - requiredStock;
    const shortageUnits = netBalance < 0 ? Math.abs(netBalance) : 0;
    const surplusUnits = netBalance > 0 ? netBalance : 0;
    const revenueImpact = Math.round((simulatedDailyDemand - baselineDailyDemand) * 7 * 6.85);
    const wasteRiskPct = Math.max(
      2.1,
      Math.min(34.5, Number(((surplusUnits / Math.max(currentOnHand, 1)) * 28 + (demandDeltaPct < 0 ? Math.abs(demandDeltaPct) * 0.25 : 0)).toFixed(1)))
    );

    const categoryComparison = [
      { category: 'Fresh Produce', baseline: 2240, simulated: Math.round(2240 * (1 + demandDeltaPct / 100) * (targetCoverageDays / 10)) },
      { category: 'Dairy & Chilled', baseline: 3780, simulated: Math.round(3780 * (1 + demandDeltaPct / 100) * (targetCoverageDays / 10)) },
      { category: 'Artisan Bakery', baseline: 1470, simulated: Math.round(1470 * (1 + demandDeltaPct / 100) * (targetCoverageDays / 10)) },
      { category: 'Fresh Seafood', baseline: 1015, simulated: Math.round(1015 * (1 + demandDeltaPct / 100) * (targetCoverageDays / 10)) },
      { category: 'Pantry & Gourmet', baseline: 1260, simulated: Math.round(1260 * (1 + demandDeltaPct / 100) * (targetCoverageDays / 10)) }
    ];

    return {
      baselineDailyDemand,
      simulatedDailyDemand,
      currentOnHand,
      requiredStock,
      shortageUnits,
      surplusUnits,
      revenueImpact,
      wasteRiskPct,
      categoryComparison
    };
  }, [demandDeltaPct, targetCoverageDays, leadTimeBufferDays]);

  // --------------------------------------------------------------------------
  // OVERVIEW CHART DATA
  // --------------------------------------------------------------------------
  const [overviewTimeframe, setOverviewTimeframe] = useState('7D');
  const overviewChartData = useMemo(() => {
    if (overviewTimeframe === '7D') {
      return [
        { label: 'Mon', actual: 4120, predicted: 4080 },
        { label: 'Tue', actual: 4390, predicted: 4420 },
        { label: 'Wed', actual: 4280, predicted: 4310 },
        { label: 'Thu', actual: 4710, predicted: 4680 },
        { label: 'Fri', actual: 5490, predicted: 5420 },
        { label: 'Sat', actual: 6180, predicted: 6110 },
        { label: 'Sun', actual: null, predicted: 5890 }
      ];
    }
    if (overviewTimeframe === '30D') {
      return [
        { label: 'Wk 1', actual: 29400, predicted: 29100 },
        { label: 'Wk 2', actual: 31200, predicted: 31500 },
        { label: 'Wk 3', actual: 30800, predicted: 30600 },
        { label: 'Wk 4', actual: null, predicted: 33400 }
      ];
    }
    return [
      { label: 'Sep', actual: 124000, predicted: 122500 },
      { label: 'Oct', actual: 131500, predicted: 132000 },
      { label: 'Nov', actual: 138900, predicted: 137800 },
      { label: 'Dec (Est)', actual: null, predicted: 156400 }
    ];
  }, [overviewTimeframe]);

  // Filtered Expiry Items
  const filteredExpiryItems = useMemo(() => {
    return expiryItems.filter((item) => {
      const status = getExpiryStatus(item.expiryDate).code;
      const matchesTab = expiryFilter === 'ALL' || status === expiryFilter;
      const q = globalSearch.trim().toLowerCase();
      const matchesSearch =
        !q ||
        item.name.toLowerCase().includes(q) ||
        item.sku.toLowerCase().includes(q) ||
        item.store.toLowerCase().includes(q);
      return matchesTab && matchesSearch;
    });
  }, [expiryItems, expiryFilter, globalSearch]);

  const expiryCounts = useMemo(() => {
    let expired = 0;
    let soon = 0;
    let safe = 0;
    expiryItems.forEach((item) => {
      const code = getExpiryStatus(item.expiryDate).code;
      if (code === 'EXPIRED') expired++;
      else if (code === 'SOON') soon++;
      else safe++;
    });
    return { expired, soon, safe, total: expiryItems.length };
  }, [expiryItems]);

  const currentBg = PAGE_BACKGROUNDS[activeTab] || PAGE_BACKGROUNDS.overview;

  return (
    <div className="min-h-screen text-slate-100 font-sans antialiased relative overflow-x-hidden selection:bg-emerald-500 selection:text-slate-950">
      {/* ====================================================================
          FULL-SCREEN HIGH-RESOLUTION SUPERMARKET PHOTOGRAPHY BACKGROUND
      ==================================================================== */}
      <div
        className="fixed inset-0 z-0 transition-all duration-700 ease-out"
        style={{
          backgroundImage: `url("${currentBg.url}"), ${currentBg.fallback}`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundAttachment: 'fixed'
        }}
      />
      {/* Subtle Dark Navy & Emerald Gradient Readability Overlay (keeps shelves clearly visible) */}
      <div
        className="fixed inset-0 z-0 pointer-events-none"
        style={{
          background:
            'linear-gradient(135deg, rgba(6, 13, 26, 0.78) 0%, rgba(8, 22, 36, 0.68) 48%, rgba(6, 15, 28, 0.82) 100%)'
        }}
      />

      {/* Floating Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-5 right-5 z-50 max-w-sm rounded-2xl bg-slate-950/90 border border-emerald-400/50 px-4 py-3.5 shadow-2xl shadow-emerald-950/60 backdrop-blur-xl flex items-start gap-3 animate-fade-in">
          <div className="mt-0.5 p-1.5 rounded-lg bg-emerald-500/20 text-emerald-400">
            <CheckCircle2 className="w-4 h-4" />
          </div>
          <div>
            <p className="text-sm font-semibold text-white">{toastMessage.title}</p>
            <p className="text-xs text-slate-300 mt-0.5">{toastMessage.detail}</p>
          </div>
        </div>
      )}

      {/* ====================================================================
          FIXED LEFT SIDEBAR NAVIGATION (EXACT 6-PAGE ORDER)
      ==================================================================== */}
      <aside
        className={`fixed top-0 left-0 bottom-0 z-40 w-72 bg-[#060e1d]/82 backdrop-blur-2xl border-r border-white/12 flex flex-col justify-between transition-transform duration-300 ${
          mobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        <div>
          {/* Brand Header */}
          <div className="px-6 py-6 border-b border-white/10 flex items-center justify-between">
            <StockWiseLogo />
            <button
              onClick={() => setMobileMenuOpen(false)}
              className="lg:hidden p-2 rounded-lg text-slate-400 hover:text-white hover:bg-white/10"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation Menu */}
          <div className="px-4 py-5">
            <div className="px-3 mb-2.5 text-[11px] font-semibold uppercase tracking-wider text-emerald-300/80">
              Platform Modules
            </div>
            <nav className="space-y-1.5">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => {
                      setActiveTab(item.id);
                      setMobileMenuOpen(false);
                    }}
                    className={`w-full flex items-center justify-between px-3.5 py-3 rounded-xl text-sm font-medium transition-all duration-200 group ${
                      isActive
                        ? 'bg-gradient-to-r from-emerald-500/25 to-emerald-600/10 text-white border border-emerald-400/45 shadow-lg shadow-emerald-950/40'
                        : 'text-slate-300 hover:text-white hover:bg-white/8 border border-transparent'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <Icon
                        className={`w-4.5 h-4.5 transition-colors ${
                          isActive ? 'text-emerald-400' : 'text-slate-400 group-hover:text-emerald-300'
                        }`}
                      />
                      <span>{item.label}</span>
                    </div>
                    {item.badge && (
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                          isActive
                            ? 'bg-emerald-400 text-slate-950'
                            : 'bg-white/10 text-emerald-300 border border-white/10'
                        }`}
                      >
                        {item.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        {/* Bottom Environment & Demo Transparency Card */}
        <div className="p-4 m-4 rounded-2xl bg-slate-950/70 border border-white/10 backdrop-blur-md">
          <div className="flex items-center gap-2 text-xs font-semibold text-emerald-300">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>Demo Sandbox Active</span>
          </div>
          <p className="text-[11px] text-slate-400 mt-1.5 leading-relaxed">
            Simulated retail telemetry & sample ML projections for interactive demonstration.
          </p>
          <div className="mt-3 pt-2.5 border-t border-white/10 flex items-center justify-between text-[11px] text-slate-300">
            <span>Backdrop View:</span>
            <span className="text-emerald-300 font-medium truncate max-w-[130px]">{currentBg.caption}</span>
          </div>
        </div>
      </aside>

      {/* ====================================================================
          MAIN CONTENT SHELL
      ==================================================================== */}
      <div className="lg:pl-72 relative z-10 min-h-screen flex flex-col">
        {/* Top Glass Header Bar */}
        <header className="sticky top-0 z-30 bg-[#060e1d]/65 backdrop-blur-xl border-b border-white/12 px-4 sm:px-8 py-3.5">
          <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <button
                onClick={() => setMobileMenuOpen(true)}
                className="lg:hidden p-2.5 rounded-xl bg-white/10 text-white hover:bg-white/15"
                aria-label="Open navigation"
              >
                <Menu className="w-5 h-5" />
              </button>

              {/* Global Search Input */}
              <div className="relative w-64 sm:w-80">
                <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={globalSearch}
                  onChange={(e) => setGlobalSearch(e.target.value)}
                  placeholder="Search SKU, product, or store..."
                  className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-950/65 border border-white/15 text-sm text-white placeholder-slate-400 focus:outline-none focus:border-emerald-400/70 transition"
                />
              </div>
            </div>

            <div className="flex items-center gap-3">
              {/* Sample Data Pill */}
              <div className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-amber-500/15 border border-amber-400/35 text-amber-200 text-xs font-medium">
                <Info className="w-3.5 h-3.5 text-amber-300" />
                <span>Sample Demonstration Data</span>
              </div>

              {/* Store Selector */}
              <select
                value={selectedStoreGlobal}
                onChange={(e) => setSelectedStoreGlobal(e.target.value)}
                className="px-3 py-2 rounded-xl bg-slate-950/75 border border-white/15 text-xs sm:text-sm text-slate-100 focus:outline-none focus:border-emerald-400"
              >
                <option value="ALL">All 4 Supermarket Stores</option>
                {STORES.map((st) => (
                  <option key={st.id} value={st.id}>
                    {st.name}
                  </option>
                ))}
              </select>

              {/* Alerts Bell */}
              <button
                onClick={() => setActiveTab('expiry')}
                className="relative p-2.5 rounded-xl bg-slate-950/65 border border-white/15 text-slate-200 hover:border-emerald-400/50 transition"
                title="View Expiry Alerts"
              >
                <Bell className="w-4 h-4" />
                <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-emerald-500 text-slate-950 text-[10px] font-bold flex items-center justify-center">
                  {expiryCounts.expired + expiryCounts.soon}
                </span>
              </button>
            </div>
          </div>
        </header>

        {/* Main Page Container */}
        <main className="flex-1 px-4 sm:px-8 py-7 max-w-7xl w-full mx-auto space-y-7">
          {/* ================================================================
              PAGE 1: OVERVIEW
          ================================================================ */}
          {activeTab === 'overview' && (
            <div className="space-y-7">
              {/* Hero Welcome Banner */}
              <section className="rounded-3xl bg-[#081326]/65 backdrop-blur-xl border border-white/15 p-6 sm:p-8 shadow-2xl relative overflow-hidden">
                <div className="absolute -right-16 -top-16 w-64 h-64 rounded-full bg-emerald-500/15 blur-3xl pointer-events-none" />
                <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6 relative z-10">
                  <div className="space-y-3 max-w-2xl">
                    <StockWiseLogo size="lg" />
                    <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white pt-1">
                      Welcome to StockWise AI
                    </h1>
                    <p className="text-lg sm:text-xl font-medium text-emerald-300">
                      Intelligent Inventory. Smarter Decisions.
                    </p>
                    <p className="text-sm text-slate-300 leading-relaxed">
                      Real-time supermarket shelf telemetry, perishable expiry OCR tracking, predictive demand modeling, and automated inter-store stock balancing across your retail network.
                    </p>
                  </div>

                  <div className="flex flex-wrap sm:flex-nowrap gap-3">
                    <button
                      onClick={() => setActiveTab('forecasting')}
                      className="px-5 py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-bold text-sm shadow-lg shadow-emerald-500/25 flex items-center gap-2 transition cursor-pointer"
                    >
                      <Sparkles className="w-4 h-4" />
                      <span>Run Demand Forecast</span>
                    </button>
                    <button
                      onClick={() => setActiveTab('expiry')}
                      className="px-5 py-3 rounded-xl bg-white/10 hover:bg-white/15 border border-white/20 text-white font-semibold text-sm flex items-center gap-2 transition cursor-pointer"
                    >
                      <ScanLine className="w-4 h-4 text-emerald-300" />
                      <span>Scan Expiry Label</span>
                    </button>
                  </div>
                </div>
              </section>

              {/* 4 Glass KPI Statistics Cards */}
              <section className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5">
                {[
                  {
                    title: 'Total Products',
                    value: selectedStoreGlobal === 'ALL' ? '14,820' : STORES.find((s) => s.id === selectedStoreGlobal)?.skus.toLocaleString(),
                    sub: '+312 SKUs synced today',
                    icon: Package,
                    accent: 'text-emerald-400',
                    onClick: () => setActiveTab('forecasting')
                  },
                  {
                    title: 'Expiry Alerts',
                    value: `${expiryCounts.expired + expiryCounts.soon} Items`,
                    sub: `${expiryCounts.expired} expired • ${expiryCounts.soon} expiring ≤ 5d`,
                    icon: AlertTriangle,
                    accent: 'text-amber-400',
                    onClick: () => setActiveTab('expiry')
                  },
                  {
                    title: 'Forecast Status',
                    value: '94.8% Acc.',
                    sub: '7-day horizon active across stores',
                    icon: TrendingUp,
                    accent: 'text-sky-400',
                    onClick: () => setActiveTab('forecasting')
                  },
                  {
                    title: 'Transfer Recommendations',
                    value: `${transfers.filter((t) => t.status === 'Recommended').length} Active`,
                    sub: 'Est. $2,480 waste prevented',
                    icon: ArrowLeftRight,
                    accent: 'text-emerald-300',
                    onClick: () => setActiveTab('transfer')
                  }
                ].map((kpi, idx) => {
                  const Icon = kpi.icon;
                  return (
                    <div
                      key={idx}
                      onClick={kpi.onClick}
                      className="cursor-pointer rounded-2xl bg-[#081326]/68 hover:bg-[#0b1b36]/80 backdrop-blur-xl border border-white/15 hover:border-emerald-400/50 p-5 shadow-xl transition-all duration-200 group"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold uppercase tracking-wider text-slate-300">
                          {kpi.title}
                        </span>
                        <div className="p-2.5 rounded-xl bg-white/8 border border-white/10 group-hover:scale-105 transition">
                          <Icon className={`w-5 h-5 ${kpi.accent}`} />
                        </div>
                      </div>
                      <div className="text-3xl font-extrabold text-white mt-3">{kpi.value}</div>
                      <div className="text-xs text-slate-300 mt-1.5 flex items-center justify-between">
                        <span>{kpi.sub}</span>
                        <ChevronRight className="w-4 h-4 text-emerald-400 opacity-0 group-hover:opacity-100 transition" />
                      </div>
                    </div>
                  );
                })}
              </section>

              {/* Main Analytics Row: Demand Forecasting Chart + Inventory Health Visualization */}
              <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Demand Forecasting Chart (2 cols) */}
                <div className="lg:col-span-2 rounded-3xl bg-[#081326]/70 backdrop-blur-xl border border-white/15 p-6 shadow-xl">
                  <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
                    <div>
                      <h2 className="text-lg font-bold text-white flex items-center gap-2">
                        <BarChart3 className="w-5 h-5 text-emerald-400" />
                        <span>Chain-Wide Demand Forecast Trajectory</span>
                      </h2>
                      <p className="text-xs text-slate-300 mt-0.5">
                        Actual POS unit velocity vs StockWise AI predicted demand (Sample Data)
                      </p>
                    </div>
                    <div className="flex items-center gap-1.5 bg-slate-950/70 p-1 rounded-xl border border-white/10">
                      {['7D', '30D', '90D'].map((tf) => (
                        <button
                          key={tf}
                          onClick={() => setOverviewTimeframe(tf)}
                          className={`px-3 py-1 rounded-lg text-xs font-semibold transition ${
                            overviewTimeframe === tf
                              ? 'bg-emerald-500 text-slate-950'
                              : 'text-slate-300 hover:text-white'
                          }`}
                        >
                          {tf}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center gap-5 text-xs mb-3">
                    <span className="flex items-center gap-2 text-emerald-300">
                      <span className="w-3 h-0.5 bg-emerald-400 inline-block" /> AI Predicted Units
                    </span>
                    <span className="flex items-center gap-2 text-sky-300">
                      <span className="w-3 h-0.5 bg-sky-400 border-b border-dashed inline-block" /> Actual POS Sales
                    </span>
                  </div>

                  <InteractiveDemandChart data={overviewChartData} height={240} />
                </div>

                {/* Inventory Health Visualization (1 col) */}
                <div className="rounded-3xl bg-[#081326]/70 backdrop-blur-xl border border-white/15 p-6 shadow-xl flex flex-col justify-between">
                  <div>
                    <h2 className="text-lg font-bold text-white flex items-center gap-2">
                      <Activity className="w-5 h-5 text-emerald-400" />
                      <span>Inventory Health Index</span>
                    </h2>
                    <p className="text-xs text-slate-300 mt-0.5">Live shelf stock distribution</p>
                  </div>

                  {/* Radial Gauge */}
                  <div className="my-5 flex items-center justify-center relative">
                    <svg className="w-44 h-44 -rotate-90" viewBox="0 0 120 120">
                      <circle cx="60" cy="60" r="48" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="12" />
                      <circle
                        cx="60"
                        cy="60"
                        r="48"
                        fill="none"
                        stroke="#10b981"
                        strokeWidth="12"
                        strokeDasharray="301.6"
                        strokeDashoffset="42"
                        strokeLinecap="round"
                      />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                      <span className="text-3xl font-extrabold text-white">88.4%</span>
                      <span className="text-[11px] font-semibold uppercase tracking-wider text-emerald-300">
                        Optimal Stock
                      </span>
                    </div>
                  </div>

                  {/* Health Breakdown Bars */}
                  <div className="space-y-2.5 text-xs">
                    {[
                      { label: 'Optimal Shelf Level', pct: 74, color: 'bg-emerald-400' },
                      { label: 'Low Stock / Reorder Soon', pct: 14, color: 'bg-sky-400' },
                      { label: 'Expiring Within 5 Days', pct: 7, color: 'bg-amber-400' },
                      { label: 'Overstock Surplus', pct: 5, color: 'bg-purple-400' }
                    ].map((row) => (
                      <div key={row.label}>
                        <div className="flex justify-between text-slate-200 mb-1">
                          <span>{row.label}</span>
                          <span className="font-bold">{row.pct}%</span>
                        </div>
                        <div className="w-full h-1.5 rounded-full bg-white/10 overflow-hidden">
                          <div className={`h-full rounded-full ${row.color}`} style={{ width: `${row.pct}%` }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </section>

              {/* Quick-Access Feature Cards (All 5 Features) */}
              <section>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-bold text-white">Intelligent Suite Quick-Access</h2>
                  <span className="text-xs text-slate-300">Click any module to launch workspace</span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                  {[
                    {
                      id: 'forecasting',
                      title: 'Demand Forecasting',
                      desc: 'AI SKU demand curves & confidence intervals',
                      icon: TrendingUp,
                      tag: '94.8% Accuracy'
                    },
                    {
                      id: 'expiry',
                      title: 'Expiry Management',
                      desc: 'OCR label scanner & perishable batch alerts',
                      icon: Clock,
                      tag: `${expiryCounts.soon + expiryCounts.expired} Alerts`
                    },
                    {
                      id: 'supplier',
                      title: 'Supplier Delay AI',
                      desc: 'Cold-chain transit risk & delay scoring',
                      icon: Truck,
                      tag: 'Experimental'
                    },
                    {
                      id: 'transfer',
                      title: 'Stock Transfer',
                      desc: 'Rebalance surplus & shortages across stores',
                      icon: ArrowLeftRight,
                      tag: '4 Routes Ready'
                    },
                    {
                      id: 'whatif',
                      title: 'What-if Analysis',
                      desc: 'Simulate demand surges & stock coverage',
                      icon: Sliders,
                      tag: 'Simulator'
                    }
                  ].map((feat) => {
                    const Icon = feat.icon;
                    return (
                      <button
                        key={feat.id}
                        onClick={() => setActiveTab(feat.id)}
                        className="text-left rounded-2xl bg-[#081326]/72 hover:bg-emerald-950/60 backdrop-blur-xl border border-white/15 hover:border-emerald-400/60 p-5 shadow-lg transition-all duration-200 flex flex-col justify-between group cursor-pointer"
                      >
                        <div>
                          <div className="flex items-center justify-between mb-3">
                            <div className="p-2.5 rounded-xl bg-emerald-500/20 text-emerald-300 border border-emerald-400/30">
                              <Icon className="w-5 h-5" />
                            </div>
                            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-white/10 text-emerald-300">
                              {feat.tag}
                            </span>
                          </div>
                          <h3 className="font-bold text-white text-sm group-hover:text-emerald-300 transition">
                            {feat.title}
                          </h3>
                          <p className="text-xs text-slate-300 mt-1.5 leading-relaxed">{feat.desc}</p>
                        </div>
                        <div className="mt-4 pt-3 border-t border-white/10 flex items-center text-xs font-semibold text-emerald-300">
                          <span>Open Module</span>
                          <ArrowRight className="w-3.5 h-3.5 ml-1.5 group-hover:translate-x-1 transition-transform" />
                        </div>
                      </button>
                    );
                  })}
                </div>
              </section>

              {/* Recent Activities Feed */}
              <section className="rounded-3xl bg-[#081326]/70 backdrop-blur-xl border border-white/15 p-6 shadow-xl">
                <h2 className="text-lg font-bold text-white mb-4">Recent Operational Intelligence</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {RECENT_ACTIVITIES.map((act) => (
                    <div
                      key={act.id}
                      className="rounded-2xl bg-slate-950/55 border border-white/10 p-4 flex items-start justify-between gap-4"
                    >
                      <div className="flex items-start gap-3">
                        <div className="mt-0.5 p-2 rounded-xl bg-emerald-500/15 text-emerald-400">
                          <Zap className="w-4 h-4" />
                        </div>
                        <div>
                          <h4 className="text-sm font-semibold text-white">{act.title}</h4>
                          <p className="text-xs text-slate-300 mt-0.5">{act.detail}</p>
                        </div>
                      </div>
                      <span className="text-[11px] text-slate-400 whitespace-nowrap">{act.time}</span>
                    </div>
                  ))}
                </div>
              </section>
            </div>
          )}

          {/* ================================================================
              PAGE 2: DEMAND FORECASTING
          ================================================================ */}
          {activeTab === 'forecasting' && (
            <div className="space-y-6">
              <div className="rounded-3xl bg-[#081326]/72 backdrop-blur-xl border border-white/15 p-6 sm:p-7 shadow-xl">
                <div className="flex flex-wrap items-center justify-between gap-4 pb-6 border-b border-white/10">
                  <div>
                    <span className="text-xs font-bold uppercase tracking-wider text-emerald-300">
                      Predictive Retail Engine
                    </span>
                    <h1 className="text-2xl sm:text-3xl font-extrabold text-white mt-1">
                      SKU Demand Forecasting
                    </h1>
                    <p className="text-sm text-slate-300 mt-1">
                      Select a supermarket SKU, target branch, and forecast horizon to compare historical actuals against AI demand projections.
                    </p>
                  </div>
                  <button
                    onClick={handleGenerateForecast}
                    disabled={fcLoading}
                    className="px-6 py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-bold text-sm shadow-lg shadow-emerald-500/25 flex items-center gap-2 transition cursor-pointer disabled:opacity-60"
                  >
                    <RefreshCw className={`w-4 h-4 ${fcLoading ? 'animate-spin' : ''}`} />
                    <span>{fcLoading ? 'Recalculating...' : 'Generate Forecast'}</span>
                  </button>
                </div>

                {/* Controls Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-6">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1.5">Product SKU</label>
                    <select
                      value={fcProduct}
                      onChange={(e) => setFcProduct(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/75 border border-white/15 text-sm text-white focus:border-emerald-400 focus:outline-none"
                    >
                      {PRODUCTS.map((p) => (
                        <option key={p.id} value={p.id}>
                          {p.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1.5">Supermarket Branch</label>
                    <select
                      value={fcStore}
                      onChange={(e) => setFcStore(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/75 border border-white/15 text-sm text-white focus:border-emerald-400 focus:outline-none"
                    >
                      {STORES.map((s) => (
                        <option key={s.id} value={s.id}>
                          {s.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1.5">Target Start Date</label>
                    <input
                      type="date"
                      value={fcDate}
                      onChange={(e) => setFcDate(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/75 border border-white/15 text-sm text-white focus:border-emerald-400 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1.5">Forecast Horizon</label>
                    <select
                      value={fcHorizon}
                      onChange={(e) => setFcHorizon(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/75 border border-white/15 text-sm text-white focus:border-emerald-400 focus:outline-none"
                    >
                      <option value="7">7 Days (Short-Term Replenishment)</option>
                      <option value="14">14 Days (Bi-Weekly Order Cycle)</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Forecast Summary KPIs */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {(() => {
                  const totalPredicted = forecastSeries.reduce((acc, d) => acc + d.predicted, 0);
                  const peakDay = [...forecastSeries].sort((a, b) => b.predicted - a.predicted)[0];
                  const selectedProd = PRODUCTS.find((p) => p.id === fcProduct) || PRODUCTS[0];
                  return [
                    { label: 'Projected Total Demand', val: `${totalPredicted.toLocaleString()} units`, sub: `Over ${fcHorizon}-day window` },
                    { label: 'Peak Demand Window', val: `${peakDay?.predicted} units`, sub: `Expected on ${peakDay?.label}` },
                    { label: 'Recommended Safety Stock', val: `${selectedProd.safetyBuffer} units`, sub: 'Prevents weekend stockout' },
                    { label: 'Model Confidence', val: '95.4%', sub: 'Sample demonstration metric' }
                  ].map((card, i) => (
                    <div key={i} className="rounded-2xl bg-[#081326]/72 backdrop-blur-xl border border-white/15 p-5">
                      <div className="text-xs font-semibold text-slate-300 uppercase">{card.label}</div>
                      <div className="text-2xl font-extrabold text-emerald-300 mt-2">{card.val}</div>
                      <div className="text-xs text-slate-400 mt-1">{card.sub}</div>
                    </div>
                  ));
                })()}
              </div>

              {/* Interactive Actual vs Predicted Chart */}
              <div className="rounded-3xl bg-[#081326]/74 backdrop-blur-xl border border-white/15 p-6 shadow-xl">
                <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
                  <div>
                    <h2 className="text-lg font-bold text-white">Actual vs. Predicted Demand Curve</h2>
                    <p className="text-xs text-slate-300">
                      Shaded emerald band illustrates 95% prediction confidence interval
                    </p>
                  </div>
                  <div className="flex items-center gap-4 text-xs">
                    <span className="flex items-center gap-1.5 text-emerald-300">
                      <span className="w-3 h-3 rounded-sm bg-emerald-400/30 border border-emerald-400" /> Predicted + 95% CI
                    </span>
                    <span className="flex items-center gap-1.5 text-sky-300">
                      <span className="w-3 h-0.5 bg-sky-400" /> Historical Actual
                    </span>
                  </div>
                </div>
                <InteractiveDemandChart data={forecastSeries} height={270} />
              </div>

              {/* Detailed Daily Breakdown Table */}
              <div className="rounded-3xl bg-[#081326]/74 backdrop-blur-xl border border-white/15 p-6 shadow-xl overflow-x-auto">
                <h3 className="text-base font-bold text-white mb-4">Daily Forecast & Variance Schedule</h3>
                <table className="w-full text-left border-collapse text-sm">
                  <thead>
                    <tr className="border-b border-white/15 text-xs uppercase text-slate-300">
                      <th className="py-3 px-4">Interval</th>
                      <th className="py-3 px-4">Actual Sales</th>
                      <th className="py-3 px-4">AI Predicted</th>
                      <th className="py-3 px-4">Confidence Range</th>
                      <th className="py-3 px-4">Suggested Order Qty</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/10">
                    {forecastSeries.map((row, idx) => (
                      <tr key={idx} className="hover:bg-white/5 transition">
                        <td className="py-3 px-4 font-semibold text-white">{row.label}</td>
                        <td className="py-3 px-4 text-sky-300">
                          {row.actual !== null ? `${row.actual} units` : 'Pending POS'}
                        </td>
                        <td className="py-3 px-4 font-bold text-emerald-300">{row.predicted} units</td>
                        <td className="py-3 px-4 text-slate-300">
                          {row.lower} – {row.upper} units
                        </td>
                        <td className="py-3 px-4">
                          <span className="px-2.5 py-1 rounded-lg bg-emerald-500/20 text-emerald-300 text-xs font-semibold">
                            +{Math.round(row.predicted * 1.05)} units
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* ================================================================
              PAGE 3: EXPIRY MANAGEMENT & OCR SCANNER
          ================================================================ */}
          {activeTab === 'expiry' && (
            <div className="space-y-6">
              {/* Top Section: OCR Scanner + Product Registration Form */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* OCR Image Upload & Expiry Date Scanner (5 cols) */}
                <div className="lg:col-span-5 rounded-3xl bg-[#081326]/74 backdrop-blur-xl border border-white/15 p-6 shadow-xl flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold uppercase tracking-wider text-emerald-300">
                        Computer Vision OCR
                      </span>
                      <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-400/30">
                        Auto-Extract
                      </span>
                    </div>
                    <h2 className="text-xl font-extrabold text-white mt-1">
                      Packaging Expiry Label Scanner
                    </h2>
                    <p className="text-xs text-slate-300 mt-1">
                      Upload a product label photo or test with a sample supermarket label preset to extract batch & expiry dates.
                    </p>

                    {/* Upload Dropzone */}
                    <label className="mt-4 block cursor-pointer rounded-2xl border-2 border-dashed border-emerald-400/45 hover:border-emerald-300 bg-slate-950/60 p-5 text-center transition relative overflow-hidden">
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handleFileUploadOcr}
                        className="hidden"
                      />
                      {isScanningOcr ? (
                        <div className="py-4 space-y-2">
                          <ScanLine className="w-9 h-9 text-emerald-400 mx-auto animate-bounce" />
                          <p className="text-sm font-bold text-emerald-300">
                            Scanning "{uploadedPreviewName}"...
                          </p>
                          <p className="text-xs text-slate-400">Extracting Lot Code & Best-Before Date</p>
                        </div>
                      ) : (
                        <div className="py-2 space-y-2">
                          <div className="w-11 h-11 rounded-xl bg-emerald-500/20 text-emerald-300 flex items-center justify-center mx-auto">
                            <Upload className="w-5 h-5" />
                          </div>
                          <p className="text-sm font-semibold text-white">
                            Click to Upload Packaging Image
                          </p>
                          <p className="text-xs text-slate-400">Supports JPG, PNG, WebP label snapshots</p>
                        </div>
                      )}
                    </label>

                    {/* Quick Sample OCR Presets */}
                    <div className="mt-4">
                      <span className="text-xs font-semibold text-slate-300 block mb-2">
                        Or simulate instant OCR scan with sample labels:
                      </span>
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                        {OCR_SCAN_PRESETS.map((preset) => (
                          <button
                            key={preset.id}
                            type="button"
                            onClick={() => triggerOcrScan(preset)}
                            className="p-2.5 rounded-xl bg-white/8 hover:bg-emerald-500/20 border border-white/12 hover:border-emerald-400/50 text-left transition cursor-pointer"
                          >
                            <div className="text-[10px] font-bold text-emerald-300">{preset.badge}</div>
                            <div className="text-xs font-semibold text-white truncate mt-0.5">{preset.label}</div>
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>

                  {ocrResultBanner && (
                    <div className="mt-4 rounded-xl bg-emerald-500/20 border border-emerald-400/45 p-3 text-xs text-emerald-200">
                      <div className="font-bold flex items-center justify-between">
                        <span>OCR Extraction Verified</span>
                        <span>{ocrResultBanner.confidence}</span>
                      </div>
                      <p className="mt-1 text-emerald-100">{ocrResultBanner.text}</p>
                    </div>
                  )}
                </div>

                {/* Product Registration Form (7 cols) */}
                <div className="lg:col-span-7 rounded-3xl bg-[#081326]/74 backdrop-blur-xl border border-white/15 p-6 shadow-xl">
                  <h2 className="text-xl font-extrabold text-white">Register Perishable Inventory Batch</h2>
                  <p className="text-xs text-slate-300 mt-1">
                    Add new arrivals manually or review OCR-populated fields before committing to shelf tracking.
                  </p>

                  {formError && (
                    <div className="mt-3 p-3 rounded-xl bg-rose-500/20 border border-rose-400/40 text-xs text-rose-200">
                      {formError}
                    </div>
                  )}

                  <form onSubmit={handleAddExpiryProduct} className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-1">Product SKU *</label>
                      <input
                        type="text"
                        placeholder="e.g., DRY-512"
                        value={newProductForm.sku}
                        onChange={(e) => setNewProductForm({ ...newProductForm, sku: e.target.value })}
                        className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/75 border border-white/15 text-sm text-white focus:border-emerald-400 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-1">Product Name *</label>
                      <input
                        type="text"
                        placeholder="e.g., Organic Meadow Butter"
                        value={newProductForm.name}
                        onChange={(e) => setNewProductForm({ ...newProductForm, name: e.target.value })}
                        className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/75 border border-white/15 text-sm text-white focus:border-emerald-400 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-1">Department Category</label>
                      <select
                        value={newProductForm.category}
                        onChange={(e) => setNewProductForm({ ...newProductForm, category: e.target.value })}
                        className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/75 border border-white/15 text-sm text-white focus:border-emerald-400 focus:outline-none"
                      >
                        <option>Dairy & Chilled</option>
                        <option>Fresh Produce</option>
                        <option>In-Store Bakery</option>
                        <option>Seafood Counter</option>
                        <option>Pantry & Gourmet</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-1">Batch / Lot Code</label>
                      <input
                        type="text"
                        placeholder="e.g., BCH-9044"
                        value={newProductForm.batch}
                        onChange={(e) => setNewProductForm({ ...newProductForm, batch: e.target.value })}
                        className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/75 border border-white/15 text-sm text-white focus:border-emerald-400 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-1">Unit Quantity *</label>
                      <input
                        type="number"
                        min="1"
                        placeholder="e.g., 64"
                        value={newProductForm.qty}
                        onChange={(e) => setNewProductForm({ ...newProductForm, qty: e.target.value })}
                        className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/75 border border-white/15 text-sm text-white focus:border-emerald-400 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-1">Expiry Date *</label>
                      <input
                        type="date"
                        value={newProductForm.expiryDate}
                        onChange={(e) => setNewProductForm({ ...newProductForm, expiryDate: e.target.value })}
                        className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/75 border border-white/15 text-sm text-white focus:border-emerald-400 focus:outline-none"
                      />
                    </div>
                    <div className="sm:col-span-2 flex flex-wrap items-center justify-between gap-4 pt-2">
                      <div className="flex-1 min-w-[200px]">
                        <label className="block text-xs font-semibold text-slate-300 mb-1">Assigned Store</label>
                        <select
                          value={newProductForm.store}
                          onChange={(e) => setNewProductForm({ ...newProductForm, store: e.target.value })}
                          className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/75 border border-white/15 text-sm text-white focus:border-emerald-400 focus:outline-none"
                        >
                          {STORES.map((s) => (
                            <option key={s.id} value={s.name}>
                              {s.name}
                            </option>
                          ))}
                        </select>
                      </div>
                      <button
                        type="submit"
                        className="mt-5 px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-bold text-sm shadow-lg shadow-emerald-500/25 flex items-center gap-2 transition cursor-pointer"
                      >
                        <Plus className="w-4 h-4" />
                        <span>Add to Inventory</span>
                      </button>
                    </div>
                  </form>
                </div>
              </div>

              {/* Filter Tabs & Inventory Expiry Table */}
              <div className="rounded-3xl bg-[#081326]/75 backdrop-blur-xl border border-white/15 p-6 shadow-xl">
                <div className="flex flex-wrap items-center justify-between gap-4 mb-5">
                  <div>
                    <h2 className="text-lg font-bold text-white">Perishable Stock Ledger</h2>
                    <p className="text-xs text-slate-300">Reference Date: Nov 26, 2026 • Real-time shelf life categorization</p>
                  </div>

                  {/* Category Filter Pills */}
                  <div className="flex flex-wrap gap-2">
                    {[
                      { id: 'ALL', label: `All Batches (${expiryCounts.total})` },
                      { id: 'EXPIRED', label: `Expired (${expiryCounts.expired})` },
                      { id: 'SOON', label: `Expiring Soon (${expiryCounts.soon})` },
                      { id: 'SAFE', label: `Safe (${expiryCounts.safe})` }
                    ].map((tab) => (
                      <button
                        key={tab.id}
                        onClick={() => setExpiryFilter(tab.id)}
                        className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition cursor-pointer ${
                          expiryFilter === tab.id
                            ? 'bg-emerald-500 text-slate-950'
                            : 'bg-slate-950/70 text-slate-300 border border-white/12 hover:text-white'
                        }`}
                      >
                        {tab.label}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse text-sm">
                    <thead>
                      <tr className="border-b border-white/15 text-xs uppercase text-slate-300">
                        <th className="py-3 px-4">SKU / Batch</th>
                        <th className="py-3 px-4">Product Name</th>
                        <th className="py-3 px-4">Store Location</th>
                        <th className="py-3 px-4">Qty</th>
                        <th className="py-3 px-4">Expiry Date</th>
                        <th className="py-3 px-4">Status</th>
                        <th className="py-3 px-4 text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/10">
                      {filteredExpiryItems.map((item) => {
                        const st = getExpiryStatus(item.expiryDate);
                        const badgeClass =
                          st.code === 'EXPIRED'
                            ? 'bg-rose-500/20 text-rose-300 border-rose-400/40'
                            : st.code === 'SOON'
                            ? 'bg-amber-500/20 text-amber-300 border-amber-400/40'
                            : 'bg-emerald-500/20 text-emerald-300 border-emerald-400/40';

                        return (
                          <tr key={item.id} className="hover:bg-white/5 transition">
                            <td className="py-3.5 px-4">
                              <div className="font-bold text-white">{item.sku}</div>
                              <div className="text-xs text-slate-400">{item.batch}</div>
                            </td>
                            <td className="py-3.5 px-4">
                              <div className="font-semibold text-white">{item.name}</div>
                              <div className="text-xs text-slate-400">{item.category}</div>
                            </td>
                            <td className="py-3.5 px-4 text-slate-200">{item.store}</td>
                            <td className="py-3.5 px-4 font-semibold text-white">{item.qty}</td>
                            <td className="py-3.5 px-4 font-mono text-xs text-slate-200">{item.expiryDate}</td>
                            <td className="py-3.5 px-4">
                              <span className={`px-2.5 py-1 rounded-full text-xs font-semibold border ${badgeClass}`}>
                                {st.label}
                              </span>
                            </td>
                            <td className="py-3.5 px-4 text-right">
                              <button
                                onClick={() => handleDeleteExpiryProduct(item.id)}
                                className="p-2 rounded-lg bg-rose-500/15 hover:bg-rose-500/30 text-rose-300 border border-rose-400/30 transition cursor-pointer"
                                title="Delete Product Batch"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </td>
                          </tr>
                        );
                      })}
                      {filteredExpiryItems.length === 0 && (
                        <tr>
                          <td colSpan="7" className="py-8 text-center text-slate-400 text-sm">
                            No perishable inventory batches match the active filter.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* ================================================================
              PAGE 4: SUPPLIER DELAY PREDICTION
          ================================================================ */}
          {activeTab === 'supplier' && (
            <div className="space-y-6">
              {/* Experimental Model Warning Banner */}
              <div className="rounded-2xl bg-amber-500/18 backdrop-blur-xl border border-amber-400/45 p-4 flex items-start gap-3.5 shadow-lg">
                <ShieldAlert className="w-6 h-6 text-amber-300 shrink-0 mt-0.5" />
                <div>
                  <h3 className="text-sm font-bold text-amber-200">
                    Experimental Predictive Logistics Model (Beta v0.9)
                  </h3>
                  <p className="text-xs text-amber-100/90 mt-0.5 leading-relaxed">
                    Delay probability estimates are generated using simulated historical carrier telemetry and synthetic weather/capacity weights. Always confirm critical cold-chain deliveries directly with dispatchers.
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Input Controls Panel (7 cols) */}
                <div className="lg:col-span-7 rounded-3xl bg-[#081326]/74 backdrop-blur-xl border border-white/15 p-6 shadow-xl space-y-5">
                  <div>
                    <h1 className="text-2xl font-extrabold text-white">Supplier Delay Risk Predictor</h1>
                    <p className="text-xs text-slate-300 mt-1">
                      Adjust shipment volume, transit distance, and carrier SLA metrics to evaluate arrival risk.
                    </p>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-1.5">Supplier Partner</label>
                      <select
                        value={supId}
                        onChange={(e) => handleSupplierChange(e.target.value)}
                        className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/75 border border-white/15 text-sm text-white focus:border-emerald-400 focus:outline-none"
                      >
                        {SUPPLIERS.map((s) => (
                          <option key={s.id} value={s.id}>
                            {s.name}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-1.5">Destination Store</label>
                      <select
                        value={supStore}
                        onChange={(e) => setSupStore(e.target.value)}
                        className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/75 border border-white/15 text-sm text-white focus:border-emerald-400 focus:outline-none"
                      >
                        {STORES.map((st) => (
                          <option key={st.id} value={st.id}>
                            {st.name}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-1.5">Shipment SKU</label>
                      <select
                        value={supProduct}
                        onChange={(e) => setSupProduct(e.target.value)}
                        className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/75 border border-white/15 text-sm text-white focus:border-emerald-400 focus:outline-none"
                      >
                        {PRODUCTS.map((p) => (
                          <option key={p.id} value={p.id}>
                            {p.name}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                        Order Quantity (Cases/Units)
                      </label>
                      <input
                        type="number"
                        min="20"
                        max="5000"
                        value={supQty}
                        onChange={(e) => setSupQty(Number(e.target.value))}
                        className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/75 border border-white/15 text-sm text-white focus:border-emerald-400 focus:outline-none"
                      />
                    </div>
                  </div>

                  {/* Interactive Sliders */}
                  <div className="space-y-4 pt-2">
                    <div>
                      <div className="flex justify-between text-xs font-semibold mb-1.5">
                        <span className="text-slate-300">Transit Distance (km)</span>
                        <span className="text-emerald-300 font-bold">{supDistance} km</span>
                      </div>
                      <input
                        type="range"
                        min="20"
                        max="650"
                        value={supDistance}
                        onChange={(e) => setSupDistance(Number(e.target.value))}
                        className="w-full accent-emerald-400 cursor-pointer"
                      />
                    </div>

                    <div>
                      <div className="flex justify-between text-xs font-semibold mb-1.5">
                        <span className="text-slate-300">Historical Supplier Reliability (%)</span>
                        <span className="text-emerald-300 font-bold">{supReliability}%</span>
                      </div>
                      <input
                        type="range"
                        min="50"
                        max="100"
                        value={supReliability}
                        onChange={(e) => setSupReliability(Number(e.target.value))}
                        className="w-full accent-emerald-400 cursor-pointer"
                      />
                    </div>

                    <div>
                      <div className="flex justify-between text-xs font-semibold mb-1.5">
                        <span className="text-slate-300">Carrier Fleet Capacity Utilization (%)</span>
                        <span className="text-emerald-300 font-bold">{supCapacity}%</span>
                      </div>
                      <input
                        type="range"
                        min="40"
                        max="100"
                        value={supCapacity}
                        onChange={(e) => setSupCapacity(Number(e.target.value))}
                        className="w-full accent-emerald-400 cursor-pointer"
                      />
                    </div>
                  </div>

                  <button
                    onClick={handlePredictDelay}
                    className="w-full py-3.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-bold text-sm shadow-lg shadow-emerald-500/25 transition cursor-pointer"
                  >
                    Predict Delay Probability
                  </button>
                </div>

                {/* Visualization & Risk Gauge Panel (5 cols) */}
                <div className="lg:col-span-5 rounded-3xl bg-[#081326]/74 backdrop-blur-xl border border-white/15 p-6 shadow-xl flex flex-col justify-between">
                  <div>
                    <h2 className="text-lg font-bold text-white">Delay Probability Assessment</h2>
                    <p className="text-xs text-slate-300 mt-0.5">Simulated arrival variance output</p>
                  </div>

                  {/* Radial Gauge */}
                  <div className="my-6 flex flex-col items-center">
                    <div className="relative w-48 h-48 flex items-center justify-center">
                      <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
                        <circle cx="60" cy="60" r="48" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="12" />
                        <circle
                          cx="60"
                          cy="60"
                          r="48"
                          fill="none"
                          stroke={
                            delayResult.riskLevel === 'High'
                              ? '#fb7185'
                              : delayResult.riskLevel === 'Moderate'
                              ? '#fbbf24'
                              : '#10b981'
                          }
                          strokeWidth="12"
                          strokeDasharray="301.6"
                          strokeDashoffset={301.6 - (301.6 * delayResult.probability) / 100}
                          strokeLinecap="round"
                          className="transition-all duration-500"
                        />
                      </svg>
                      <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <span className="text-4xl font-extrabold text-white">{delayResult.probability}%</span>
                        <span
                          className={`text-xs font-bold uppercase mt-1 px-2.5 py-0.5 rounded-full ${
                            delayResult.riskLevel === 'High'
                              ? 'bg-rose-500/25 text-rose-300'
                              : delayResult.riskLevel === 'Moderate'
                              ? 'bg-amber-500/25 text-amber-300'
                              : 'bg-emerald-500/25 text-emerald-300'
                          }`}
                        >
                          {delayResult.riskLevel} Risk
                        </span>
                      </div>
                    </div>

                    <div className="mt-3 text-center">
                      <span className="text-xs text-slate-300">Estimated Schedule Slippage: </span>
                      <span className="text-sm font-bold text-white">+{delayResult.estDelayHours} Hours</span>
                    </div>
                  </div>

                  {/* Risk Factor Breakdown */}
                  <div className="space-y-3 bg-slate-950/60 rounded-2xl p-4 border border-white/10">
                    <div className="text-xs font-bold uppercase tracking-wider text-slate-300">
                      Key Risk Drivers
                    </div>
                    {delayResult.factors.map((f) => (
                      <div key={f.label}>
                        <div className="flex justify-between text-xs mb-1">
                          <span className="text-slate-200">{f.label}</span>
                          <span className="font-bold text-emerald-300">{f.score}/100</span>
                        </div>
                        <div className="w-full h-1.5 rounded-full bg-white/10 overflow-hidden">
                          <div
                            className="h-full rounded-full bg-gradient-to-r from-emerald-400 to-amber-400 transition-all duration-500"
                            style={{ width: `${f.score}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* ================================================================
              PAGE 5: INTER-STORE STOCK TRANSFER
          ================================================================ */}
          {activeTab === 'transfer' && (
            <div className="space-y-6">
              {/* Store Network Overview Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {STORES.map((st) => (
                  <div
                    key={st.id}
                    className="rounded-2xl bg-[#081326]/74 backdrop-blur-xl border border-white/15 p-5 shadow-lg"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-emerald-300">{st.id}</span>
                      <span className="text-xs text-slate-400">{st.district}</span>
                    </div>
                    <h3 className="font-bold text-white text-base mt-1">{st.name}</h3>
                    <div className="mt-4 grid grid-cols-2 gap-2 text-xs">
                      <div className="p-2.5 rounded-xl bg-emerald-500/15 border border-emerald-400/30">
                        <div className="text-slate-300">Surplus</div>
                        <div className="text-base font-extrabold text-emerald-300">+{st.surplus} u</div>
                      </div>
                      <div className="p-2.5 rounded-xl bg-amber-500/15 border border-amber-400/30">
                        <div className="text-slate-300">Shortage</div>
                        <div className="text-base font-extrabold text-amber-300">-{st.shortage} u</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Donor & Receiver Selector + Interactive Store Transfer Visualization */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Route Builder (5 cols) */}
                <div className="lg:col-span-5 rounded-3xl bg-[#081326]/74 backdrop-blur-xl border border-white/15 p-6 shadow-xl space-y-4">
                  <h2 className="text-xl font-extrabold text-white">Rebalance Store Inventory</h2>
                  <p className="text-xs text-slate-300">
                    Pair a high-surplus donor store with a low-stock receiver branch to prevent stockouts and overstock waste.
                  </p>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                      Donor Store (Surplus Source)
                    </label>
                    <select
                      value={donorStoreId}
                      onChange={(e) => setDonorStoreId(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/75 border border-white/15 text-sm text-white focus:border-emerald-400 focus:outline-none"
                    >
                      {STORES.map((s) => (
                        <option key={s.id} value={s.id}>
                          {s.name} (Surplus: +{s.surplus} units)
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                      Receiver Store (Shortage Destination)
                    </label>
                    <select
                      value={receiverStoreId}
                      onChange={(e) => setReceiverStoreId(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/75 border border-white/15 text-sm text-white focus:border-emerald-400 focus:outline-none"
                    >
                      {STORES.map((s) => (
                        <option key={s.id} value={s.id}>
                          {s.name} (Shortage: -{s.shortage} units)
                        </option>
                      ))}
                    </select>
                  </div>

                  <button
                    onClick={handleCreateCustomTransfer}
                    className="w-full py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-bold text-sm shadow-lg shadow-emerald-500/25 transition cursor-pointer"
                  >
                    Generate Transfer Proposal
                  </button>
                </div>

                {/* Interactive SVG Store Network Visualization (7 cols) */}
                <div className="lg:col-span-7 rounded-3xl bg-[#081326]/74 backdrop-blur-xl border border-white/15 p-6 shadow-xl flex flex-col justify-between">
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <h2 className="text-lg font-bold text-white">Metro Store Transfer Topology</h2>
                      <p className="text-xs text-slate-300">Live surplus-to-shortage directional flow visualization</p>
                    </div>
                    <span className="px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-semibold">
                      Active Corridor
                    </span>
                  </div>

                  <svg viewBox="0 0 600 220" className="w-full h-auto my-2">
                    {/* Connecting Corridor Lines */}
                    <line x1="120" y1="60" x2="460" y2="60" stroke="rgba(16,185,129,0.35)" strokeWidth="3" strokeDasharray="6 4" />
                    <line x1="120" y1="165" x2="460" y2="165" stroke="rgba(16,185,129,0.35)" strokeWidth="3" strokeDasharray="6 4" />
                    <line x1="120" y1="60" x2="460" y2="165" stroke="rgba(56,189,248,0.4)" strokeWidth="2.5" />
                    <line x1="120" y1="165" x2="460" y2="60" stroke="rgba(56,189,248,0.4)" strokeWidth="2.5" />

                    {/* Store Nodes */}
                    {[
                      { id: 'ST-01', name: 'Downtown #01', role: 'DONOR (+310)', x: 120, y: 60, color: '#10b981' },
                      { id: 'ST-03', name: 'Harborview #03', role: 'DONOR (+245)', x: 120, y: 165, color: '#10b981' },
                      { id: 'ST-02', name: 'Westside #02', role: 'RECEIVER (-185)', x: 460, y: 60, color: '#fbbf24' },
                      { id: 'ST-04', name: 'Northgate #04', role: 'RECEIVER (-220)', x: 460, y: 165, color: '#fbbf24' }
                    ].map((node) => {
                      const isHighlighted = node.id === donorStoreId || node.id === receiverStoreId;
                      return (
                        <g key={node.id}>
                          <rect
                            x={node.x - 95}
                            y={node.y - 28}
                            width="190"
                            height="56"
                            rx="14"
                            fill="rgba(6, 14, 29, 0.9)"
                            stroke={isHighlighted ? '#34d399' : 'rgba(255,255,255,0.2)'}
                            strokeWidth={isHighlighted ? '2.5' : '1.2'}
                          />
                          <circle cx={node.x - 74} cy={node.y} r="7" fill={node.color} />
                          <text x={node.x - 58} y={node.y - 4} fill="#ffffff" fontSize="12" fontWeight="700">
                            {node.name}
                          </text>
                          <text x={node.x - 58} y={node.y + 13} fill={node.color} fontSize="10" fontWeight="600">
                            {node.role}
                          </text>
                        </g>
                      );
                    })}

                    {/* Center Hub Badge */}
                    <rect x="242" y="92" width="116" height="36" rx="18" fill="#10b981" />
                    <text x="300" y="114" textAnchor="middle" fill="#041019" fontSize="11" fontWeight="800">
                      AI ROUTE ENGINE
                    </text>
                  </svg>
                </div>
              </div>

              {/* Transfer Recommendation Table */}
              <div className="rounded-3xl bg-[#081326]/75 backdrop-blur-xl border border-white/15 p-6 shadow-xl overflow-x-auto">
                <h2 className="text-lg font-bold text-white mb-4">AI Stock Transfer Recommendations</h2>
                <table className="w-full text-left border-collapse text-sm">
                  <thead>
                    <tr className="border-b border-white/15 text-xs uppercase text-slate-300">
                      <th className="py-3 px-4">Product</th>
                      <th className="py-3 px-4">Donor → Receiver</th>
                      <th className="py-3 px-4">Surplus / Shortage</th>
                      <th className="py-3 px-4">Transfer Qty</th>
                      <th className="py-3 px-4">Distance</th>
                      <th className="py-3 px-4 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/10">
                    {transfers.map((trf) => (
                      <tr key={trf.id} className="hover:bg-white/5 transition">
                        <td className="py-3.5 px-4">
                          <div className="font-bold text-white">{trf.product}</div>
                          <div className="text-xs text-slate-400">{trf.sku} • {trf.id}</div>
                        </td>
                        <td className="py-3.5 px-4">
                          <div className="text-emerald-300 font-medium">{trf.donor}</div>
                          <div className="text-xs text-amber-300">→ {trf.receiver}</div>
                        </td>
                        <td className="py-3.5 px-4 text-xs">
                          <span className="text-emerald-300 font-bold">+{trf.donorSurplus}</span> /{' '}
                          <span className="text-amber-300 font-bold">-{trf.receiverShortage}</span>
                        </td>
                        <td className="py-3.5 px-4 font-extrabold text-white">{trf.recommendedQty} units</td>
                        <td className="py-3.5 px-4 text-slate-300">{trf.distanceKm} km</td>
                        <td className="py-3.5 px-4 text-right">
                          {trf.status === 'Dispatched' ? (
                            <span className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl bg-emerald-500/20 text-emerald-300 text-xs font-bold border border-emerald-400/40">
                              <CheckCircle2 className="w-3.5 h-3.5" /> Dispatched
                            </span>
                          ) : (
                            <button
                              onClick={() => handleApproveTransfer(trf.id)}
                              className="px-3.5 py-1.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold transition cursor-pointer"
                            >
                              Approve Transfer
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* ================================================================
              PAGE 6: WHAT-IF ANALYSIS
          ================================================================ */}
          {activeTab === 'whatif' && (
            <div className="space-y-6">
              {/* Scenario Presets & Interactive Sliders */}
              <div className="rounded-3xl bg-[#081326]/74 backdrop-blur-xl border border-white/15 p-6 sm:p-7 shadow-xl">
                <div className="flex flex-wrap items-center justify-between gap-4 pb-5 border-b border-white/10">
                  <div>
                    <span className="text-xs font-bold uppercase tracking-wider text-emerald-300">
                      Strategic Simulation Sandbox
                    </span>
                    <h1 className="text-2xl sm:text-3xl font-extrabold text-white mt-1">
                      What-if Demand & Coverage Simulator
                    </h1>
                    <p className="text-xs text-slate-300 mt-1">
                      Stress-test supermarket inventory buffers against promotional spikes, seasonal rushes, or supply disruptions.
                    </p>
                  </div>

                  {/* Quick Scenario Preset Buttons */}
                  <div className="flex flex-wrap gap-2">
                    <button
                      onClick={() => {
                        setDemandDeltaPct(45);
                        setTargetCoverageDays(14);
                        setLeadTimeBufferDays(4);
                      }}
                      className="px-3.5 py-2 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-200 border border-emerald-400/40 text-xs font-semibold cursor-pointer"
                    >
                      Holiday Rush (+45%)
                    </button>
                    <button
                      onClick={() => {
                        setDemandDeltaPct(15);
                        setTargetCoverageDays(18);
                        setLeadTimeBufferDays(7);
                      }}
                      className="px-3.5 py-2 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 text-amber-200 border border-amber-400/40 text-xs font-semibold cursor-pointer"
                    >
                      Supply Disruption
                    </button>
                    <button
                      onClick={() => {
                        setDemandDeltaPct(0);
                        setTargetCoverageDays(10);
                        setLeadTimeBufferDays(2);
                      }}
                      className="px-3.5 py-2 rounded-xl bg-white/10 hover:bg-white/15 text-slate-200 border border-white/15 text-xs font-semibold cursor-pointer"
                    >
                      Reset Baseline
                    </button>
                  </div>
                </div>

                {/* Sliders Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6">
                  <div className="rounded-2xl bg-slate-950/60 border border-white/10 p-4">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-xs font-semibold text-slate-300">Demand Surge / Drop (%)</span>
                      <span className="text-base font-extrabold text-emerald-300">
                        {demandDeltaPct > 0 ? `+${demandDeltaPct}%` : `${demandDeltaPct}%`}
                      </span>
                    </div>
                    <input
                      type="range"
                      min="-40"
                      max="80"
                      value={demandDeltaPct}
                      onChange={(e) => setDemandDeltaPct(Number(e.target.value))}
                      className="w-full accent-emerald-400 cursor-pointer"
                    />
                    <div className="flex justify-between text-[10px] text-slate-400 mt-1">
                      <span>-40% Slump</span>
                      <span>0% Baseline</span>
                      <span>+80% Surge</span>
                    </div>
                  </div>

                  <div className="rounded-2xl bg-slate-950/60 border border-white/10 p-4">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-xs font-semibold text-slate-300">Target Stock Coverage</span>
                      <span className="text-base font-extrabold text-emerald-300">{targetCoverageDays} Days</span>
                    </div>
                    <input
                      type="range"
                      min="3"
                      max="25"
                      value={targetCoverageDays}
                      onChange={(e) => setTargetCoverageDays(Number(e.target.value))}
                      className="w-full accent-emerald-400 cursor-pointer"
                    />
                    <div className="flex justify-between text-[10px] text-slate-400 mt-1">
                      <span>3d Lean</span>
                      <span>12d Standard</span>
                      <span>25d Buffer</span>
                    </div>
                  </div>

                  <div className="rounded-2xl bg-slate-950/60 border border-white/10 p-4">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-xs font-semibold text-slate-300">Supplier Lead Buffer</span>
                      <span className="text-base font-extrabold text-emerald-300">+{leadTimeBufferDays} Days</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="10"
                      value={leadTimeBufferDays}
                      onChange={(e) => setLeadTimeBufferDays(Number(e.target.value))}
                      className="w-full accent-emerald-400 cursor-pointer"
                    />
                    <div className="flex justify-between text-[10px] text-slate-400 mt-1">
                      <span>0d JIT</span>
                      <span>5d Safe</span>
                      <span>10d Max</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Impact Output Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="rounded-2xl bg-[#081326]/74 backdrop-blur-xl border border-white/15 p-5">
                  <div className="text-xs font-semibold text-slate-300 uppercase">Simulated Daily Demand</div>
                  <div className="text-2xl font-extrabold text-white mt-2">
                    {whatIfMetrics.simulatedDailyDemand.toLocaleString()} u/day
                  </div>
                  <div className="text-xs text-slate-400 mt-1">
                    Baseline: {whatIfMetrics.baselineDailyDemand.toLocaleString()} u/day
                  </div>
                </div>

                <div className="rounded-2xl bg-[#081326]/74 backdrop-blur-xl border border-white/15 p-5">
                  <div className="text-xs font-semibold text-slate-300 uppercase">Projected Stockout Shortage</div>
                  <div
                    className={`text-2xl font-extrabold mt-2 ${
                      whatIfMetrics.shortageUnits > 0 ? 'text-rose-400' : 'text-emerald-400'
                    }`}
                  >
                    {whatIfMetrics.shortageUnits.toLocaleString()} units
                  </div>
                  <div className="text-xs text-slate-400 mt-1">
                    {whatIfMetrics.shortageUnits > 0 ? 'Additional replenishment needed' : 'Zero stockout exposure'}
                  </div>
                </div>

                <div className="rounded-2xl bg-[#081326]/74 backdrop-blur-xl border border-white/15 p-5">
                  <div className="text-xs font-semibold text-slate-300 uppercase">Projected Holding Surplus</div>
                  <div className="text-2xl font-extrabold text-sky-300 mt-2">
                    {whatIfMetrics.surplusUnits.toLocaleString()} units
                  </div>
                  <div className="text-xs text-slate-400 mt-1">
                    Spoilage / Waste Risk: {whatIfMetrics.wasteRiskPct}%
                  </div>
                </div>

                <div className="rounded-2xl bg-[#081326]/74 backdrop-blur-xl border border-white/15 p-5">
                  <div className="text-xs font-semibold text-slate-300 uppercase">7-Day Revenue Delta</div>
                  <div
                    className={`text-2xl font-extrabold mt-2 ${
                      whatIfMetrics.revenueImpact >= 0 ? 'text-emerald-300' : 'text-amber-300'
                    }`}
                  >
                    {whatIfMetrics.revenueImpact >= 0
                      ? `+$${whatIfMetrics.revenueImpact.toLocaleString()}`
                      : `-$${Math.abs(whatIfMetrics.revenueImpact).toLocaleString()}`}
                  </div>
                  <div className="text-xs text-slate-400 mt-1">Vs. baseline weekly run-rate</div>
                </div>
              </div>

              {/* Interactive Scenario Comparison Bar Visualization */}
              <div className="rounded-3xl bg-[#081326]/74 backdrop-blur-xl border border-white/15 p-6 shadow-xl">
                <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
                  <div>
                    <h2 className="text-lg font-bold text-white">Baseline vs. What-If Required Stock by Department</h2>
                    <p className="text-xs text-slate-300">
                      Visualizing required inventory commitment across supermarket aisles
                    </p>
                  </div>
                  <div className="flex items-center gap-4 text-xs">
                    <span className="flex items-center gap-1.5 text-slate-300">
                      <span className="w-3 h-3 rounded bg-slate-500" /> Baseline Plan
                    </span>
                    <span className="flex items-center gap-1.5 text-emerald-300">
                      <span className="w-3 h-3 rounded bg-emerald-400" /> Simulated Scenario
                    </span>
                  </div>
                </div>

                <div className="space-y-4">
                  {whatIfMetrics.categoryComparison.map((cat) => {
                    const maxBar = Math.max(cat.baseline, cat.simulated, 6000);
                    const basePct = Math.min(100, Math.round((cat.baseline / maxBar) * 100));
                    const simPct = Math.min(100, Math.round((cat.simulated / maxBar) * 100));

                    return (
                      <div key={cat.category} className="space-y-1.5">
                        <div className="flex justify-between text-xs">
                          <span className="font-bold text-white">{cat.category}</span>
                          <span className="text-slate-300">
                            Baseline: <strong>{cat.baseline.toLocaleString()}u</strong> → Simulated:{' '}
                            <strong className="text-emerald-300">{cat.simulated.toLocaleString()}u</strong>
                          </span>
                        </div>
                        <div className="space-y-1">
                          <div className="w-full h-2.5 rounded-full bg-white/10 overflow-hidden">
                            <div
                              className="h-full rounded-full bg-slate-400 transition-all duration-300"
                              style={{ width: `${basePct}%` }}
                            />
                          </div>
                          <div className="w-full h-2.5 rounded-full bg-white/10 overflow-hidden">
                            <div
                              className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-teal-300 transition-all duration-300"
                              style={{ width: `${simPct}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}