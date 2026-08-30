const OPTIONS = [
  {
    id: "voice",
    icon: "mic",
    title: "Voice Interaction",
    description: "Speak naturally. baatचीत will listen to your voice and respond audibly.",
  },
  {
    id: "text",
    icon: "keyboard",
    title: "Text & Visual",
    description: "Type your thoughts. baatचीत will respond with text and gentle visual aids.",
  },
];

export default function ModeSelect({ onContinue }) {
  return (
    <div className="min-h-screen relative flex flex-col antialiased overflow-x-hidden">
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-primary-container/10 blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-5%] w-[40%] h-[60%] rounded-full bg-secondary-container/20 blur-[100px]" />
      </div>

      <main className="relative z-10 flex flex-col items-center justify-center min-h-screen px-margin-mobile md:px-margin-desktop py-section-gap w-full max-w-screen-lg mx-auto">
        <header className="text-center mb-12 md:mb-section-gap max-w-2xl">
          <h1 className="text-headline-lg-mobile md:text-display-lg text-on-surface mb-4 tracking-tight">
            How would you like to communicate?
          </h1>
          <p className="text-body-lg text-on-surface-variant">
            Choose whichever feels comfortable right now -- you can switch
            anytime during your session.
          </p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-gutter md:gap-8 w-full max-w-3xl">
          {OPTIONS.map((option) => (
            <button
              key={option.id}
              onClick={() => onContinue(option.id)}
              className="group relative flex flex-col items-center text-center p-8 md:p-12 rounded-3xl transition-all duration-500 hover:-translate-y-1 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-4 focus:ring-offset-background bg-surface-container/70 backdrop-blur-xl border border-white/10 hover:border-primary/60"
            >
              <div className="w-20 h-20 mb-6 rounded-full flex items-center justify-center transition-colors duration-300 bg-surface-container-high group-hover:bg-primary-container">
                <span
                  className="material-symbols-outlined text-4xl transition-transform duration-500 group-hover:scale-110 text-primary group-hover:text-on-primary-container"
                  style={{ fontVariationSettings: "'FILL' 1" }}
                >
                  {option.icon}
                </span>
              </div>
              <h2 className="text-headline-md mb-3 text-on-surface group-hover:text-primary">
                {option.title}
              </h2>
              <p className="text-body-md text-on-surface-variant">{option.description}</p>
            </button>
          ))}
        </div>
      </main>
    </div>
  );
}
