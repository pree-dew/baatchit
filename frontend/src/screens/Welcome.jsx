import BlobBackground from "../components/BlobBackground.jsx";

export default function Welcome({ onBegin }) {
  return (
    <div className="min-h-screen relative flex flex-col antialiased">
      <BlobBackground />

      <main className="flex-grow flex flex-col justify-center items-center px-container-padding-mobile md:px-container-padding-desktop py-section-gap">
        <div className="w-full max-w-md flex flex-col items-center">
          <div className="mb-12 text-center fade-slide-up">
            <span
              className="material-symbols-outlined text-primary text-[48px] mb-4 block"
              style={{ fontVariationSettings: "'FILL' 1" }}
            >
              spa
            </span>
            <h1 className="text-headline-lg-mobile md:text-headline-lg text-primary tracking-tight font-bold">
              baatचीत
            </h1>
          </div>

          <div className="text-center mb-16 fade-slide-up delay-100">
            <h2 className="text-display-lg text-on-surface mb-4">
              Welcome to your space for healing.
            </h2>
            <p className="text-body-lg text-on-surface-variant max-w-[280px] mx-auto">
              Tap begin whenever you're ready to talk. No sign-up, no account
              -- just you and a moment of space.
            </p>
          </div>

          <div className="w-full space-y-4 fade-slide-up delay-200">
            <button
              onClick={onBegin}
              className="w-full bg-primary/90 hover:bg-primary text-on-primary text-label-md py-4 px-6 rounded-full transition-all duration-300 shadow-[0_10px_30px_rgba(190,216,193,0.1)] hover:shadow-[0_15px_40px_rgba(190,216,193,0.15)] hover:-translate-y-1 flex items-center justify-center gap-3"
            >
              <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 0" }}>
                mic
              </span>
              Begin
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
