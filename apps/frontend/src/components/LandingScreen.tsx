interface LandingScreenProps {
  onEnter: () => void;
}

/**
 * A lightweight brand/entry screen. It does not perform real authentication
 * -- per the bootcamp's own video guidance, login/signup screens are not a
 * priority for evaluation -- but gives the product a visible "front door"
 * before the dashboard, which matters for how the demo video reads and for
 * anyone browsing the deployed app cold.
 */
export function LandingScreen({ onEnter }: LandingScreenProps) {
  return (
    <main className="relative min-h-screen overflow-hidden bg-[#0f1f16] text-white">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 opacity-40"
        style={{
          backgroundImage:
            "radial-gradient(circle at 20% 20%, rgba(31,138,91,0.35), transparent 45%), radial-gradient(circle at 80% 0%, rgba(183,121,31,0.25), transparent 40%)",
        }}
      />

      <div className="relative mx-auto flex min-h-screen max-w-5xl flex-col items-center justify-center px-6 py-16 text-center">
        <svg
          width="132"
          height="132"
          viewBox="0 0 132 132"
          role="img"
          aria-label="CarbonPilot AI logo"
          className="mb-8"
        >
          <title>CarbonPilot AI</title>
          <defs>
            <linearGradient id="hexfade" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#2fae7a" />
              <stop offset="100%" stopColor="#123b2a" />
            </linearGradient>
            <clipPath id="hexclip">
              <path d="M66 8 L118 38 L118 92 L66 122 L14 92 L14 38 Z" />
            </clipPath>
          </defs>
          <path d="M66 8 L118 38 L118 92 L66 122 L14 92 L14 38 Z" fill="url(#hexfade)" />
          <g clipPath="url(#hexclip)">
            <rect x="14" y="86" width="12" height="40" fill="#0b2a1d" />
            <rect x="32" y="72" width="12" height="54" fill="#0b2a1d" />
            <rect x="50" y="60" width="10" height="66" fill="#0b2a1d" />
            <circle cx="54" cy="50" r="6" fill="#123b2a" />
            <path
              d="M66 96 C52 91 45 74 57 60 C62 74 66 65 76 70 C81 82 76 94 66 96 Z"
              fill="#d9f2c4"
            />
          </g>
          <circle cx="104" cy="26" r="3.5" fill="#e0ac4f" />
          <circle cx="118" cy="38" r="3.5" fill="#e0ac4f" />
          <circle cx="110" cy="54" r="3.5" fill="#e0ac4f" />
          <path
            d="M104 26 L118 38 L110 54"
            stroke="#e0ac4f"
            strokeWidth="1.4"
            fill="none"
          />
        </svg>

        <p className="mb-3 text-xs font-semibold uppercase tracking-[0.35em] text-emerald-300/80">
          Karbon Muhasebesi Platformu
        </p>
        <h1 className="text-4xl font-bold tracking-tight text-white sm:text-6xl">
          CarbonPilot AI
        </h1>
        <p className="mt-5 max-w-2xl text-base text-emerald-50/80 sm:text-lg">
          Ağır sanayi ihracatçıları için yapay zeka destekli CBAM/SKDM uyumluluk ve
          karbon karar destek platformu.
        </p>

        <div className="mt-10 flex flex-wrap items-center justify-center gap-3 text-xs font-medium text-emerald-100/90">
          <span className="rounded-full border border-emerald-400/30 bg-emerald-400/10 px-4 py-1.5">
            CBAM / SKDM Uyumlu
          </span>
          <span className="rounded-full border border-emerald-400/30 bg-emerald-400/10 px-4 py-1.5">
            Gemini + LangGraph Agent
          </span>
          <span className="rounded-full border border-emerald-400/30 bg-emerald-400/10 px-4 py-1.5">
            Denetlenebilir Rapor
          </span>
        </div>

        <button
          type="button"
          onClick={onEnter}
          className="mt-12 inline-flex items-center gap-2 rounded-lg bg-emerald-400 px-8 py-3.5 text-sm font-semibold text-[#0f1f16] shadow-lg shadow-emerald-900/40 transition-transform hover:scale-[1.02] hover:bg-emerald-300"
        >
          Panele Git
          <span aria-hidden="true">&rarr;</span>
        </button>
      </div>
    </main>
  );
}