import Link from "next/link";
import { Activity, ArrowRight, BarChart3, CheckCircle2, Clock, Dumbbell, HeartPulse, Lock, Salad, Sparkles, Star, Trophy, Utensils } from "lucide-react";

const stats = [
  { value: "18 min", label: "daily planning saved" },
  { value: "92%", label: "plans adjusted weekly" },
  { value: "4.8/5", label: "coach clarity rating" },
];

const pillars = [
  {
    icon: HeartPulse,
    title: "Biometric onboarding",
    body: "Age, height, weight, schedule, activity level, constraints, and goals become one live coaching profile.",
  },
  {
    icon: Dumbbell,
    title: "Adaptive workouts",
    body: "Strength, mobility, conditioning, and recovery sessions tune around equipment, time, soreness, and progress.",
  },
  {
    icon: Salad,
    title: "Nutrition that fits work",
    body: "Meal targets, practical prep ideas, macro ranges, and logging flows built for calendars packed with meetings.",
  },
];

const weeklyFlow = ["Biometrics", "Goal", "Plan", "Log", "Adjust"];

const meals = [
  { name: "Power breakfast", cals: 430, protein: "34g" },
  { name: "Desk lunch", cals: 610, protein: "48g" },
  { name: "Late lift dinner", cals: 720, protein: "56g" },
];

export default function HomePage() {
  return (
    <main className="min-h-screen overflow-hidden bg-[#0b100d] text-[#f5f1df]">
      <section className="relative isolate px-6 py-8 sm:px-10 lg:px-16">
        <div className="absolute inset-0 -z-20 bg-[radial-gradient(circle_at_18%_20%,rgba(151,255,92,0.22),transparent_28%),radial-gradient(circle_at_88%_8%,rgba(255,196,87,0.18),transparent_24%),linear-gradient(135deg,#0b100d_0%,#111a13_44%,#1c2418_100%)]" />
        <div className="absolute inset-0 -z-10 opacity-[0.13] [background-image:linear-gradient(90deg,#f5f1df_1px,transparent_1px),linear-gradient(#f5f1df_1px,transparent_1px)] [background-size:44px_44px]" />
        <div className="absolute left-1/2 top-16 -z-10 h-80 w-80 -translate-x-1/2 rounded-full bg-lime-300/10 blur-3xl" />

        <nav className="mx-auto flex max-w-7xl items-center justify-between rounded-full border border-[#f5f1df]/15 bg-[#0b100d]/55 px-5 py-3 shadow-2xl shadow-black/20 backdrop-blur-xl">
          <Link href="/" className="flex items-center gap-3" aria-label="PulseForge home">
            <span className="grid h-10 w-10 place-items-center rounded-full bg-lime-300 text-[#0b100d] shadow-[0_0_28px_rgba(190,242,100,0.35)]">
              <Activity className="h-5 w-5" aria-hidden="true" />
            </span>
            <span className="font-serif text-xl tracking-tight">PulseForge</span>
          </Link>
          <div className="hidden items-center gap-7 text-sm text-[#d8d2b8]/80 md:flex">
            <a className="transition hover:text-lime-200" href="#features">Features</a>
            <a className="transition hover:text-lime-200" href="#dashboard">Dashboard</a>
            <a className="transition hover:text-lime-200" href="#pricing">Pricing</a>
          </div>
          <Link
            href="/sign-up"
            className="rounded-full bg-[#f5f1df] px-5 py-2.5 text-sm font-semibold text-[#0b100d] transition hover:bg-lime-200 focus:outline-none focus:ring-2 focus:ring-lime-300 focus:ring-offset-2 focus:ring-offset-[#0b100d]"
          >
            Start coaching
          </Link>
        </nav>

        <div className="mx-auto grid max-w-7xl items-center gap-12 pb-16 pt-20 lg:grid-cols-[1.05fr_0.95fr] lg:pb-24 lg:pt-28">
          <div>
            <div className="mb-8 inline-flex items-center gap-3 rounded-full border border-lime-200/25 bg-lime-200/10 px-4 py-2 text-sm text-lime-100">
              <Sparkles className="h-4 w-4" aria-hidden="true" />
              AI fitness coach for calendars with no mercy
            </div>
            <h1 className="max-w-4xl font-serif text-6xl leading-[0.9] tracking-[-0.055em] text-[#fff9df] sm:text-7xl lg:text-8xl">
              Fitness plans that survive real work weeks.
            </h1>
            <p className="mt-7 max-w-2xl text-lg leading-8 text-[#d8d2b8] sm:text-xl">
              PulseForge turns biometrics, goals, meals, workouts, and progress logs into weekly coaching that adapts before busy professionals fall off track.
            </p>
            <div className="mt-10 flex flex-col gap-4 sm:flex-row">
              <Link
                href="/sign-up"
                className="group inline-flex items-center justify-center gap-3 rounded-full bg-lime-300 px-7 py-4 font-bold text-[#0b100d] shadow-[0_16px_60px_rgba(190,242,100,0.28)] transition hover:-translate-y-0.5 hover:bg-lime-200 focus:outline-none focus:ring-2 focus:ring-lime-200 focus:ring-offset-2 focus:ring-offset-[#0b100d]"
              >
                Build my first plan
                <ArrowRight className="h-5 w-5 transition group-hover:translate-x-1" aria-hidden="true" />
              </Link>
              <Link
                href="/sign-in"
                className="inline-flex items-center justify-center rounded-full border border-[#f5f1df]/20 px-7 py-4 font-semibold text-[#fff9df] transition hover:border-lime-200/60 hover:bg-white/5 focus:outline-none focus:ring-2 focus:ring-lime-200 focus:ring-offset-2 focus:ring-offset-[#0b100d]"
              >
                View demo dashboard
              </Link>
            </div>
            <div className="mt-12 grid max-w-2xl grid-cols-3 gap-3">
              {stats.map((stat) => (
                <div key={stat.label} className="rounded-3xl border border-[#f5f1df]/12 bg-[#f5f1df]/7 p-4 backdrop-blur">
                  <div className="font-serif text-3xl text-lime-200">{stat.value}</div>
                  <div className="mt-1 text-xs uppercase tracking-[0.18em] text-[#d8d2b8]/70">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="relative mx-auto w-full max-w-xl lg:max-w-none">
            <div className="absolute -left-8 top-10 h-24 w-24 rounded-[2rem] bg-[#ffc457] blur-2xl" />
            <div className="absolute -right-10 bottom-24 h-36 w-36 rounded-full bg-lime-300/30 blur-3xl" />
            <div className="relative rotate-1 rounded-[2.5rem] border border-[#f5f1df]/18 bg-[#151d15]/85 p-4 shadow-2xl shadow-black/45 backdrop-blur-xl">
              <div className="rounded-[2rem] border border-[#f5f1df]/10 bg-[#0e150f] p-5">
                <div className="flex items-center justify-between border-b border-[#f5f1df]/10 pb-5">
                  <div>
                    <p className="text-sm uppercase tracking-[0.24em] text-lime-200/80">Today coach</p>
                    <h2 className="mt-1 font-serif text-3xl">Lean strength block</h2>
                  </div>
                  <div className="rounded-2xl bg-lime-300 px-4 py-3 text-center text-[#0b100d]">
                    <div className="text-2xl font-black">42</div>
                    <div className="text-xs font-bold uppercase">min</div>
                  </div>
                </div>

                <div className="mt-5 grid gap-4 sm:grid-cols-2">
                  <div className="rounded-3xl bg-[#f5f1df] p-5 text-[#0b100d]">
                    <div className="flex items-center gap-2 text-sm font-bold uppercase tracking-[0.16em] text-[#36502b]">
                      <Dumbbell className="h-4 w-4" aria-hidden="true" /> Workout
                    </div>
                    <p className="mt-5 text-4xl font-black tracking-tight">Upper Push</p>
                    <p className="mt-2 text-sm text-[#36502b]">Superset format. Hotel gym friendly. Shoulder-safe swaps ready.</p>
                  </div>
                  <div className="rounded-3xl border border-[#f5f1df]/12 bg-[#1d281a] p-5">
                    <div className="flex items-center gap-2 text-sm font-bold uppercase tracking-[0.16em] text-lime-200">
                      <Utensils className="h-4 w-4" aria-hidden="true" /> Nutrition
                    </div>
                    <p className="mt-5 text-4xl font-black tracking-tight">2,180</p>
                    <p className="mt-2 text-sm text-[#d8d2b8]/75">cal target with 168g protein and low-prep dinner option.</p>
                  </div>
                </div>

                <div className="mt-4 rounded-3xl border border-[#f5f1df]/12 bg-[#121a12] p-5">
                  <div className="mb-4 flex items-center justify-between">
                    <div>
                      <p className="text-sm uppercase tracking-[0.2em] text-[#d8d2b8]/70">Weekly adaptation</p>
                      <p className="mt-1 text-lg font-semibold">Plan updates after 4 logs</p>
                    </div>
                    <BarChart3 className="h-6 w-6 text-lime-200" aria-hidden="true" />
                  </div>
                  <div className="flex items-center gap-2">
                    {weeklyFlow.map((step, index) => (
                      <div key={step} className="flex flex-1 items-center gap-2">
                        <div className={`h-2 flex-1 rounded-full ${index < 4 ? "bg-lime-300" : "bg-[#f5f1df]/15"}`} />
                        <span className="sr-only">{step}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="features" className="bg-[#f5f1df] px-6 py-20 text-[#0b100d] sm:px-10 lg:px-16">
        <div className="mx-auto max-w-7xl">
          <div className="max-w-3xl">
            <p className="text-sm font-black uppercase tracking-[0.24em] text-[#5a6c31]">Coaching engine</p>
            <h2 className="mt-4 font-serif text-5xl leading-none tracking-[-0.04em] sm:text-6xl">One profile. Two generators. Daily feedback loop.</h2>
          </div>
          <div className="mt-12 grid gap-5 lg:grid-cols-3">
            {pillars.map((pillar) => {
              const Icon = pillar.icon;
              return (
                <article key={pillar.title} className="group rounded-[2rem] border border-[#0b100d]/10 bg-white/55 p-7 shadow-sm transition hover:-translate-y-1 hover:bg-white">
                  <div className="grid h-14 w-14 place-items-center rounded-2xl bg-[#0b100d] text-lime-200 transition group-hover:rotate-3 group-hover:scale-105">
                    <Icon className="h-7 w-7" aria-hidden="true" />
                  </div>
                  <h3 className="mt-8 font-serif text-3xl tracking-[-0.03em]">{pillar.title}</h3>
                  <p className="mt-4 leading-7 text-[#3c4635]">{pillar.body}</p>
                </article>
              );
            })}
          </div>
        </div>
      </section>

      <section id="dashboard" className="relative bg-[#dfe8bd] px-6 py-20 text-[#0b100d] sm:px-10 lg:px-16">
        <div className="absolute inset-x-0 top-0 h-px bg-[#0b100d]/15" />
        <div className="mx-auto grid max-w-7xl gap-10 lg:grid-cols-[0.9fr_1.1fr]">
          <div>
            <p className="text-sm font-black uppercase tracking-[0.24em] text-[#5a6c31]">Progress command center</p>
            <h2 className="mt-4 font-serif text-5xl leading-none tracking-[-0.04em] sm:text-6xl">Know what changed, not just what happened.</h2>
            <p className="mt-6 text-lg leading-8 text-[#3f4a34]">Workout logs, meal entries, adherence streaks, biometric deltas, and weekly summaries show why plan changed and what next week demands.</p>
          </div>
          <div className="grid gap-5 md:grid-cols-2">
            <div className="rounded-[2rem] bg-[#0b100d] p-6 text-[#f5f1df] shadow-2xl shadow-[#0b100d]/20">
              <div className="flex items-center justify-between">
                <h3 className="font-serif text-3xl">Meal log</h3>
                <Clock className="h-6 w-6 text-lime-200" aria-hidden="true" />
              </div>
              <div className="mt-6 space-y-3">
                {meals.map((meal) => (
                  <div key={meal.name} className="flex items-center justify-between rounded-2xl bg-white/8 p-4">
                    <div>
                      <p className="font-semibold">{meal.name}</p>
                      <p className="text-sm text-[#d8d2b8]/70">{meal.protein} protein</p>
                    </div>
                    <p className="font-black text-lime-200">{meal.cals}</p>
                  </div>
                ))}
              </div>
            </div>
            <div className="rounded-[2rem] border border-[#0b100d]/10 bg-[#f5f1df] p-6 shadow-xl shadow-[#0b100d]/10">
              <div className="flex items-center justify-between">
                <h3 className="font-serif text-3xl">Week score</h3>
                <Trophy className="h-6 w-6 text-[#6b7d2a]" aria-hidden="true" />
              </div>
              <div className="mt-8 grid place-items-center rounded-full border-[18px] border-lime-300 bg-[#0b100d] p-12 text-center text-[#f5f1df]">
                <p className="font-serif text-6xl">87</p>
                <p className="text-sm uppercase tracking-[0.2em] text-lime-100">steady cut</p>
              </div>
              <p className="mt-6 leading-7 text-[#3f4a34]">Coach recommends one lower-body deload and higher-carb lunch before Thursday lift.</p>
            </div>
          </div>
        </div>
      </section>

      <section id="pricing" className="bg-[#0b100d] px-6 py-20 text-[#f5f1df] sm:px-10 lg:px-16">
        <div className="mx-auto grid max-w-7xl gap-8 lg:grid-cols-[1fr_0.8fr]">
          <div className="rounded-[2.5rem] border border-[#f5f1df]/12 bg-[#151d15] p-8 sm:p-10">
            <div className="flex flex-wrap items-start justify-between gap-6">
              <div>
                <p className="text-sm font-black uppercase tracking-[0.24em] text-lime-200">Premium tier</p>
                <h2 className="mt-4 font-serif text-5xl tracking-[-0.04em]">Personal coaching without personal-trainer overhead.</h2>
              </div>
              <div className="rounded-3xl bg-lime-300 p-5 text-[#0b100d]">
                <span className="font-serif text-5xl">$19</span>
                <span className="font-bold">/mo</span>
              </div>
            </div>
            <div className="mt-10 grid gap-4 sm:grid-cols-2">
              {[
                "Unlimited AI workout plans",
                "Unlimited AI nutrition plans",
                "Weekly summary and plan revision",
                "Meal and exercise logging",
                "Progress dashboard",
                "Priority biometric recalculation",
              ].map((feature) => (
                <div key={feature} className="flex items-center gap-3 rounded-2xl bg-white/6 p-4">
                  <CheckCircle2 className="h-5 w-5 flex-none text-lime-200" aria-hidden="true" />
                  <span>{feature}</span>
                </div>
              ))}
            </div>
          </div>
          <aside className="rounded-[2.5rem] bg-[#f5f1df] p-8 text-[#0b100d] sm:p-10">
            <div className="flex items-center gap-2 text-[#6b7d2a]">
              {[0, 1, 2, 3, 4].map((item) => (
                <Star key={item} className="h-5 w-5 fill-current" aria-hidden="true" />
              ))}
            </div>
            <blockquote className="mt-8 font-serif text-4xl leading-tight tracking-[-0.035em]">
              “It stopped giving me fantasy plans and started fitting training into my actual calendar.”
            </blockquote>
            <p className="mt-6 text-[#3f4a34]">Built for professionals who need concise direction, fast logging, and adjustments when life breaks perfect routines.</p>
            <Link
              href="/sign-up"
              className="mt-10 inline-flex w-full items-center justify-center gap-3 rounded-full bg-[#0b100d] px-7 py-4 font-bold text-[#f5f1df] transition hover:bg-[#24341e] focus:outline-none focus:ring-2 focus:ring-[#0b100d] focus:ring-offset-2 focus:ring-offset-[#f5f1df]"
            >
              Start premium trial
              <Lock className="h-5 w-5" aria-hidden="true" />
            </Link>
          </aside>
        </div>
      </section>
    </main>
  );
}
