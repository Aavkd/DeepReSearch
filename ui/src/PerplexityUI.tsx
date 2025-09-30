import React, { useEffect, useMemo, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Switch } from "@/components/ui/switch";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Search as SearchIcon,
  Loader2,
  Globe2,
  Settings,
  History,
  Copy,
  Check,
  Moon,
  Sun,
  RefreshCw,
  StopCircle,
  Sparkles,
  BookOpenText,
  Database,
  Shield,
  Cpu,
} from "lucide-react";

// ---------- Types matching your backend contracts ----------
export type Source = {
  title: string;
  url: string;
  published?: string | null;
  snippet: string;
  relevance?: number;
};

export type Diagnostics = {
  searchProvider?: string;
  llm?: string;
  latencyMs?: number;
  cached?: boolean;
  tokens?: { prompt?: number; completion?: number } | null;
  notes?: string;
};

export type SearchResponse = {
  answer: string;
  bullets: string[];
  sources: Source[];
  diagnostics: Diagnostics;
};

export type SearchRequest = {
  query: string;
  maxResults?: number;
  locale?: string;
  timeRange?: string; // e.g., "7d", "30d"
  strict?: boolean;
  forceLocal?: boolean; // prefer Ollama
  includeDomains?: string[];
  excludeDomains?: string[];
  ui?: { mode?: "concise" | "full" };
  selectedModel?: string; // Override the default model
  selectedProvider?: "openrouter" | "ollama"; // Override the provider
};

export type ModelInfo = {
  openrouter: {
    configured: string | null;
    available: string[];
    error?: string;
  };
  ollama: {
    configured: string;
    available: string[];
    error?: string;
  };
};

// ---------- Helpers ----------
const API_BASE = (import.meta as any).env?.VITE_API_BASE || ""; // e.g., http://localhost:8080

function domainOf(url: string) {
  try {
    const u = new URL(url);
    return u.hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
}

function classNames(...xs: (string | false | null | undefined)[]) {
  return xs.filter(Boolean).join(" ");
}

// ---------- Main UI ----------
export default function PerplexityLikeFrontend() {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState<"search" | "summarize" | "learn">("search");
  const [locale, setLocale] = useState("en");
  const [timeRange, setTimeRange] = useState("30d");
  const [maxResults, setMaxResults] = useState(6);
  const [forceLocal, setForceLocal] = useState(false);
  const [strict, setStrict] = useState(true);
  const [includeDomains, setIncludeDomains] = useState<string>("");
  const [excludeDomains, setExcludeDomains] = useState<string>("");

  const [resp, setResp] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [models, setModels] = useState<ModelInfo | null>(null);
  const [modelsLoading, setModelsLoading] = useState(false);
  const [modelDialogOpen, setModelDialogOpen] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState<"openrouter" | "ollama">("ollama");
  const [selectedModel, setSelectedModel] = useState<string>("");
  const abortRef = useRef<AbortController | null>(null);

  const placeholder = useMemo(() => {
    if (mode === "search") return "Demandez n'importe quoi…";
    if (mode === "summarize") return "Collez un lien pour résumer…";
    return "Je veux apprendre… (ex: LLMs, SSL, économie)";
  }, [mode]);

  const runSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    setResp(null);
    const controller = new AbortController();
    abortRef.current = controller;

    const payload: SearchRequest = {
      query: query.trim(),
      maxResults,
      locale,
      timeRange,
      strict,
      forceLocal,
      includeDomains: includeDomains
        .split(/[,\s]+/)
        .map((s) => s.trim())
        .filter(Boolean),
      excludeDomains: excludeDomains
        .split(/[,\s]+/)
        .map((s) => s.trim())
        .filter(Boolean),
      ui: { mode: "concise" },
      selectedModel: selectedModel || undefined,
      selectedProvider: selectedModel ? selectedProvider : undefined,
    };

    try {
      const r = await fetch(`${API_BASE}/api/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data = (await r.json()) as SearchResponse;
      setResp(data);
    } catch (e: any) {
      if (e.name === "AbortError") return;
      setError(e.message || "Unexpected error");
    } finally {
      setLoading(false);
      abortRef.current = null;
    }
  };

  const stop = () => {
    abortRef.current?.abort();
    abortRef.current = null;
    setLoading(false);
  };

  const copyAnswer = async () => {
    if (!resp) return;
    const text = [resp.answer, "", ...resp.bullets.map((b) => `• ${b}`), "", "Sources:", ...resp.sources.map((s, i) => `${i + 1}. ${s.title} — ${s.url}`)].join("\n");
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1400);
  };

  const fetchModels = async () => {
    setModelsLoading(true);
    try {
      const r = await fetch(`${API_BASE}/api/models`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data = await r.json() as ModelInfo;
      setModels(data);
    } catch (e: any) {
      console.error("Failed to fetch models:", e);
    } finally {
      setModelsLoading(false);
    }
  };

  const openModelDialog = () => {
    setModelDialogOpen(true);
    if (!models) {
      fetchModels();
    }
  };

  const selectModel = (provider: "openrouter" | "ollama", model: string) => {
    setSelectedProvider(provider);
    setSelectedModel(model);
    
    // Update forceLocal based on provider selection
    if (provider === "ollama") {
      setForceLocal(true);
    } else if (provider === "openrouter") {
      setForceLocal(false);
    }
    
    setModelDialogOpen(false);
  };

  const getCurrentModel = () => {
    if (!models) return "Chargement...";
    
    if (forceLocal && models.ollama.available.length > 0) {
      return selectedModel || models.ollama.configured;
    } else if (!forceLocal && models.openrouter.available.length > 0) {
      return selectedModel || models.openrouter.configured || "Non configuré";
    }
    
    return "Aucun modèle disponible";
  };

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Background flourish */}
      <div className="pointer-events-none fixed inset-0 opacity-70 [background:radial-gradient(1000px_600px_at_50%_-200px,rgba(120,119,198,.12),transparent_60%)]"/>

      <div className="flex">
        {/* Left rail */}
        <nav className="hidden md:flex flex-col items-center gap-6 w-16 pt-6 border-r border-white/5">          
          <div className="text-lg font-semibold">✳️</div>
          <IconButton label="Accueil" icon={<History className="h-5 w-5"/>}/>
          <IconButton label="Découvrir" icon={<Globe2 className="h-5 w-5"/>}/>
          <IconButton label="Espaces" icon={<Database className="h-5 w-5"/>}/>
          <div className="mt-auto pb-6 flex flex-col items-center gap-4">
            <ThemeToggle/>
            <IconButton label="Paramètres" icon={<Settings className="h-5 w-5"/>}/>
          </div>
        </nav>

        {/* Main column */}
        <main className="flex-1 px-4 md:px-8 lg:px-16">
          {/* Centered header */}
          <div className="mx-auto max-w-3xl pt-20 md:pt-28 text-center">
            <h1 className="text-5xl md:text-6xl font-semibold tracking-tight mb-10 select-none">perplexity</h1>

            {/* Search bar */}
            <Card className="bg-white/5 backdrop-blur border-white/10">
              <CardContent className="p-3 md:p-4">
                <div className="flex items-center gap-2">
                  <SearchIcon className="h-5 w-5 opacity-70"/>
                  <input
                    className="flex-1 bg-transparent outline-none placeholder:text-white/40 text-sm md:text-base"
                    placeholder={placeholder}
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && runSearch()}
                  />
                  <Button onClick={runSearch} disabled={loading} size="sm" className="rounded-xl">
                    {loading ? <Loader2 className="h-4 w-4 animate-spin"/> : <SearchIcon className="h-4 w-4"/>}
                  </Button>
                </div>

                {/* Quick chips */}
                <div className="mt-3 flex flex-wrap items-center gap-2">
                  <Chip active={mode === "search"} onClick={() => setMode("search")} icon={<Globe2 className="h-3.5 w-3.5"/>}>
                    Explorer
                  </Chip>
                  <Chip active={mode === "summarize"} onClick={() => setMode("summarize")} icon={<Sparkles className="h-3.5 w-3.5"/>}>
                    Résumer
                  </Chip>
                  <Chip active={mode === "learn"} onClick={() => setMode("learn")} icon={<BookOpenText className="h-3.5 w-3.5"/>}>
                    Apprendre
                  </Chip>

                  <Separator className="mx-2 h-5 bg-white/10" orientation="vertical"/>
                  <div className="flex items-center gap-2 text-xs text-white/70">
                    <Shield className="h-3.5 w-3.5"/>
                    <span>Strict</span>
                    <Switch checked={strict} onCheckedChange={setStrict}/>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-white/70">
                    <Database className="h-3.5 w-3.5"/>
                    <span>Local</span>
                    <Switch checked={forceLocal} onCheckedChange={setForceLocal}/>
                  </div>
                  
                  <Dialog open={modelDialogOpen} onOpenChange={setModelDialogOpen}>
                    <DialogTrigger asChild>
                      <button
                        onClick={openModelDialog}
                        className="flex items-center gap-2 text-xs text-white/70 hover:text-white/90 transition-colors max-w-40"
                      >
                        <Cpu className="h-3.5 w-3.5 flex-shrink-0"/>
                        <div className="flex flex-col items-start">
                          <span>Modèles</span>
                          <span className="text-xs text-white/50 truncate">
                            {getCurrentModel()}
                          </span>
                        </div>
                      </button>
                    </DialogTrigger>
                    <DialogContent className="bg-gray-900 border-gray-700 text-white max-w-2xl">
                      <DialogHeader>
                        <DialogTitle className="text-xl font-semibold">Modèles disponibles</DialogTitle>
                      </DialogHeader>
                      <div className="space-y-6 mt-4">
                        {modelsLoading ? (
                          <div className="flex items-center justify-center py-8">
                            <Loader2 className="h-6 w-6 animate-spin"/>
                            <span className="ml-2">Chargement des modèles...</span>
                          </div>
                        ) : models ? (
                          <>
                            {/* OpenRouter Models */}
                            <div className="space-y-3">
                              <h3 className="text-lg font-medium text-green-400 flex items-center gap-2">
                                <Globe2 className="h-4 w-4"/>
                                OpenRouter
                              </h3>
                              {models.openrouter.configured ? (
                                <button
                                  onClick={() => selectModel("openrouter", models.openrouter.configured!)}
                                  className={`w-full text-left bg-gray-800 rounded-lg p-4 hover:bg-gray-700 transition-colors border-2 ${
                                    selectedProvider === "openrouter" && (selectedModel === models.openrouter.configured || (!selectedModel && !forceLocal))
                                      ? "border-green-500" : "border-transparent"
                                  }`}
                                >
                                  <div className="text-sm font-mono text-green-300">
                                    {models.openrouter.configured}
                                  </div>
                                  <div className="text-xs text-gray-400 mt-2 flex items-center gap-2">
                                    ✓ Configuré dans .env
                                    {selectedProvider === "openrouter" && (selectedModel === models.openrouter.configured || (!selectedModel && !forceLocal)) && (
                                      <span className="text-green-400">• Sélectionné</span>
                                    )}
                                  </div>
                                </button>
                              ) : (
                                <div className="bg-gray-800 rounded-lg p-4 opacity-50">
                                  <div className="text-sm text-gray-400">
                                    {models.openrouter.error || "Non configuré"}
                                  </div>
                                  <div className="text-xs text-gray-500 mt-2">
                                    Définir OPENROUTER_API_KEY et OPENROUTER_MODEL dans .env
                                  </div>
                                </div>
                              )}
                            </div>
                            
                            {/* Ollama Models */}
                            <div className="space-y-3">
                              <h3 className="text-lg font-medium text-blue-400 flex items-center gap-2">
                                <Database className="h-4 w-4"/>
                                Ollama
                                {models.ollama.available.length > 0 && (
                                  <span className="text-xs bg-blue-900 px-2 py-1 rounded">
                                    Modèles installés ({models.ollama.available.length}) :
                                  </span>
                                )}
                              </h3>
                              <div className="space-y-2 max-h-64 overflow-y-auto">
                                {models.ollama.available.length > 0 ? (
                                  models.ollama.available.map((model, index) => {
                                    const isSelected = selectedProvider === "ollama" && (selectedModel === model || (!selectedModel && forceLocal && model === models.ollama.configured));
                                    const isDefault = model === models.ollama.configured;
                                    
                                    return (
                                      <button
                                        key={index}
                                        onClick={() => selectModel("ollama", model)}
                                        className={`w-full text-left bg-gray-800 rounded-lg p-3 hover:bg-gray-700 transition-colors border-2 ${
                                          isSelected ? "border-blue-500" : "border-transparent"
                                        }`}
                                      >
                                        <div className="text-sm font-mono text-blue-300">
                                          {model}
                                        </div>
                                        <div className="text-xs mt-1 flex items-center gap-2">
                                          {isDefault && (
                                            <span className="text-green-400 flex items-center gap-1">
                                              <span className="w-2 h-2 bg-green-400 rounded-full"></span>
                                              Configuré par défaut
                                            </span>
                                          )}
                                          {isSelected && (
                                            <span className="text-blue-400">• Sélectionné</span>
                                          )}
                                        </div>
                                      </button>
                                    );
                                  })
                                ) : (
                                  <div className="bg-gray-800 rounded-lg p-4">
                                    {models.ollama.error ? (
                                      <div className="text-sm text-red-400 mb-2">
                                        ⚠️ {models.ollama.error}
                                      </div>
                                    ) : (
                                      <div className="text-sm text-gray-400 mb-2">
                                        Aucun modèle Ollama détecté.
                                      </div>
                                    )}
                                    <div className="text-xs text-gray-500 mt-2">
                                      Pour installer des modèles: <code className="bg-gray-700 px-2 py-1 rounded">ollama pull llama2</code>
                                    </div>
                                  </div>
                                )}
                              </div>
                            </div>
                          </>
                        ) : (
                          <div className="text-center py-8">
                            <p className="text-gray-400">Impossible de charger les modèles</p>
                          </div>
                        )}
                      </div>
                    </DialogContent>
                  </Dialog>
                </div>
              </CardContent>
            </Card>

            {/* Advanced filters */}
            <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
              <Filter label="Langue">
                <select className="bg-white/5 rounded-lg px-3 py-2 outline-none" value={locale} onChange={(e) => setLocale(e.target.value)}>
                  <option value="en">English</option>
                  <option value="fr">Français</option>
                  <option value="es">Español</option>
                  <option value="de">Deutsch</option>
                </select>
              </Filter>
              <Filter label="Période">
                <select className="bg-white/5 rounded-lg px-3 py-2 outline-none" value={timeRange} onChange={(e) => setTimeRange(e.target.value)}>
                  <option value="7d">7 jours</option>
                  <option value="30d">30 jours</option>
                  <option value="365d">1 an</option>
                  <option value="all">Tout</option>
                </select>
              </Filter>
              <Filter label="Résultats">
                <select className="bg-white/5 rounded-lg px-3 py-2 outline-none" value={maxResults} onChange={(e) => setMaxResults(parseInt(e.target.value))}>
                  {[3,4,5,6,8,10,12].map(n => <option key={n} value={n}>{n}</option>)}
                </select>
              </Filter>
            </div>

            <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
              <input
                className="bg-white/5 rounded-lg px-3 py-2 outline-none placeholder:text-white/40"
                placeholder="Inclure domaines (ex: nasa.gov, esa.int)"
                value={includeDomains}
                onChange={(e) => setIncludeDomains(e.target.value)}
              />
              <input
                className="bg-white/5 rounded-lg px-3 py-2 outline-none placeholder:text-white/40"
                placeholder="Exclure domaines (ex: reddit.com)"
                value={excludeDomains}
                onChange={(e) => setExcludeDomains(e.target.value)}
              />
            </div>
          </div>

          {/* Results */}
          <div className="mx-auto max-w-3xl mt-8 pb-24">
            {error && (
              <Card className="bg-red-500/10 border-red-500/30">
                <CardContent className="p-4 text-sm">
                  <div className="font-semibold mb-1">Erreur</div>
                  <div className="opacity-90">{error}</div>
                </CardContent>
              </Card>
            )}

            {loading && (
              <Card className="mt-4 bg-white/5 border-white/10 animate-pulse">
                <CardHeader className="p-4">Recherche en cours…</CardHeader>
                <CardContent className="p-4 space-y-3">
                  <div className="h-4 bg-white/10 rounded"/>
                  <div className="h-4 bg-white/10 rounded w-2/3"/>
                  <div className="h-4 bg-white/10 rounded w-4/5"/>
                </CardContent>
                <CardFooter className="p-4 flex gap-2">
                  <Button variant="secondary" size="sm" onClick={stop}>
                    <StopCircle className="h-4 w-4 mr-2"/>Stop
                  </Button>
                </CardFooter>
              </Card>
            )}

            {resp && (
              <Card className="mt-4 bg-white/5 border-white/10">
                <CardHeader className="p-4 flex flex-col gap-3">
                  <div className="flex items-center gap-2 text-xs text-white/60">
                    <Badge variant="secondary" className="bg-white/10">{resp.diagnostics.searchProvider ?? "search"}</Badge>
                    <span>↔</span>
                    <Badge variant="secondary" className="bg-white/10">{resp.diagnostics.llm ?? "llm"}</Badge>
                    <span>•</span>
                    <span>{resp.diagnostics.cached ? "cache" : `${resp.diagnostics.latencyMs ?? ""} ms`}</span>
                  </div>

                  <div className="text-lg leading-relaxed whitespace-pre-wrap">{resp.answer}</div>

                  {resp.bullets?.length > 0 && (
                    <ul className="list-disc pl-6 space-y-1 text-white/90">
                      {resp.bullets.map((b, i) => (
                        <li key={i}>{b}</li>
                      ))}
                    </ul>
                  )}
                </CardHeader>

                <CardContent className="p-4">
                  <div className="text-xs font-medium uppercase tracking-wider text-white/50 mb-2">
                    Sources
                  </div>
                  <div className="space-y-3">
                    {resp.sources?.map((s, i) => (
                      <div key={i} className="flex items-start gap-3">
                        <Badge variant="secondary" className="mt-0.5 bg-white/10">{i + 1}</Badge>
                        <div className="min-w-0">
                          <a
                            className="block text-sm text-blue-300 hover:underline truncate"
                            href={s.url}
                            target="_blank"
                            rel="noreferrer"
                          >
                            {s.title || domainOf(s.url)}
                          </a>
                          <div className="text-xs text-white/60 truncate">
                            {domainOf(s.url)} {s.published ? `• ${new Date(s.published).toLocaleDateString()}` : ""}
                          </div>
                          <div className="text-xs text-white/70 line-clamp-2">
                            {s.snippet}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>

                <CardFooter className="p-4 flex gap-2">
                  <Button variant="secondary" size="sm" onClick={copyAnswer}>
                    {copied ? <Check className="h-4 w-4 mr-2"/> : <Copy className="h-4 w-4 mr-2"/>}
                    {copied ? "Copié" : "Copier"}
                  </Button>
                  <Button variant="secondary" size="sm" onClick={runSearch} disabled={loading}>
                    {loading ? <Loader2 className="h-4 w-4 mr-2 animate-spin"/> : <RefreshCw className="h-4 w-4 mr-2"/>}
                    Régénérer
                  </Button>
                </CardFooter>
              </Card>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

// ---------- Small UI atoms ----------
function IconButton({ label, icon }: { label: string; icon: React.ReactNode }) {
  return (
    <button
      className="relative inline-grid place-items-center h-10 w-10 rounded-xl hover:bg-white/5 text-white/80"
      title={label}
    >
      {icon}
    </button>
  );
}

function Chip({ children, active, onClick, icon }: { children: React.ReactNode; active?: boolean; onClick?: () => void; icon?: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      className={classNames(
        "inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs",
        active ? "bg-white text-black" : "bg-white/10 hover:bg-white/20 text-white/90"
      )}
    >
      {icon}
      {children}
    </button>
  );
}

function Filter({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between bg-white/5 rounded-xl px-3 py-2">
      <span className="text-xs text-white/60">{label}</span>
      {children}
    </div>
  );
}

function ThemeToggle() {
  const [dark, setDark] = useState(true);
  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);
  return (
    <button
      onClick={() => setDark(!dark)}
      className="inline-grid place-items-center h-10 w-10 rounded-xl hover:bg-white/5 text-white/80"
      title="Thème"
    >
      {dark ? <Moon className="h-5 w-5"/> : <Sun className="h-5 w-5"/>}
    </button>
  );
}