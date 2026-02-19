# DESIGN SYSTEM - FELIXOVERSE

> **Contexto**: Este documento é um guia de padronização extraído do código-fonte do portfólio FelixoVerse. Ele cataloga todos os padrões visuais, estruturais e técnicos utilizados no projeto, servindo como referência oficial para manter consistência em futuras implementações e novos projetos que sigam a mesma identidade visual.
>
> **Objetivo**: Transformar decisões de design implícitas no código em um sistema documentado e reutilizável, facilitando a manutenção, escalabilidade e colaboração.
>
> **Stack**: React 18 + Tailwind CSS 3 + Framer Motion 10 + Vite

---

## 1. IDENTIDADE VISUAL

### 1.1 Paleta de Cores

#### Cores Primárias

| Nome | Código | Uso Principal |
|------|--------|---------------|
| **Felixo Purple** | `#C084FC` | Cor de marca estática, textos de destaque |
| **Felixo Purple Bright** | `#A855F7` | Cor de marca vibrante, efeitos de glow |
| **Branco** | `#FFFFFF` | Textos principais, ícones |
| **Preto Puro** | `#000000` | Fundo base |

#### Cores de Fundo (Gradientes)

| Nome | Código | Uso |
|------|--------|-----|
| **Zinc 950** | `rgb(9, 9, 11)` | Fundo principal escuro |
| **Zinc 900** | `rgb(24, 24, 27)` | Cards, containers |
| **Zinc 800** | `rgb(39, 39, 42)` | Inputs, elementos secundários |
| **Black/Zinc Gradient** | `from-black via-zinc-950 to-black` | Fundo da aplicação |

#### Cores de Texto

| Nome | Código | Uso |
|------|--------|-----|
| **Zinc 50** | `rgb(250, 250, 250)` | Texto principal |
| **Zinc 300** | `rgb(212, 212, 216)` | Texto secundário |
| **Zinc 400** | `rgb(161, 161, 170)` | Texto terciário, placeholders |
| **Zinc 500** | `rgb(113, 113, 122)` | Texto desabilitado |

#### Cores de Tecnologias (Badges)

| Tecnologia | Cor | Código |
|------------|-----|--------|
| HTML | Laranja | `#E34F26` |
| CSS | Azul | `#1572B6` |
| JavaScript | Amarelo | `#F7DF1E` |
| TypeScript | Azul TS | `#3178C6` |
| Python | Azul Python | `#3776AB` |
| React | Ciano | `#61DAFB` |
| Tailwind | Ciano Claro | `#06B6D4` |
| Vite | Roxo Vite | `#646CFF` |
| C# | Roxo Escuro | `#512BD4` |
| Django | Verde Escuro | `#0C4B33` |
| Git | Vermelho | `#F05032` |

#### Cores de Status

| Status | Cor de Fundo | Cor de Texto | Borda |
|--------|--------------|--------------|-------|
| **Finalizado** | `bg-green-950/80` | `text-green-300` | `border-green-700/60` |
| **Em Desenvolvimento** | `bg-yellow-400/20` | `text-yellow-100` | `border-yellow-400/40` |

#### Cores de Categoria

| Categoria | Background | Texto | Borda |
|-----------|------------|-------|-------|
| Web | `bg-blue-500/10` | `text-blue-400` | `border-blue-500/20` |
| Code | `bg-green-500/10` | `text-green-400` | `border-green-500/20` |
| Music | `bg-pink-500/10` | `text-pink-400` | `border-pink-500/20` |
| Design | `bg-purple-500/10` | `text-purple-400` | `border-purple-500/20` |
| Game | `bg-orange-500/10` | `text-orange-400` | `border-orange-500/20` |
| Automation | `bg-yellow-500/10` | `text-yellow-400` | `border-yellow-500/20` |

### 1.2 Tipografia

#### Fonte Principal
- **Família**: `'Space Grotesk', sans-serif`
- **Aplicação**: Todo o sistema

#### Hierarquia de Tamanhos

| Elemento | Tamanho Desktop | Tamanho Mobile | Peso |
|----------|----------------|----------------|------|
| **H1 (Hero)** | `text-5xl` (48px) | `text-4xl` (36px) | `font-bold` (700) |
| **H2 (Seções)** | `text-3xl` (30px) | `text-2xl` (24px) | `font-bold` (700) |
| **H3 (Cards)** | `text-base` (16px) | `text-base` (16px) | `font-bold` (700) |
| **Body** | `text-base` (16px) | `text-base` (16px) | `font-normal` (400) |
| **Body Large** | `text-lg` (18px) | `text-base` (16px) | `font-normal` (400) |
| **Small** | `text-sm` (14px) | `text-sm` (14px) | `font-medium` (500) |
| **Extra Small** | `text-xs` (12px) | `text-xs` (12px) | `font-medium` (500) |
| **Mono (Timer)** | `font-mono` | `font-mono` | `font-bold` (700) |

#### Espaçamento de Linhas
- **Títulos**: `leading-tight` (1.25)
- **Parágrafos**: `leading-relaxed` (1.625)

### 1.3 Contraste e Hierarquia Visual

#### Opacidades Padrão
- **Bordas Sutis**: `border-white/5` (5%)
- **Bordas Padrão**: `border-white/10` (10%)
- **Bordas Hover**: `border-white/20` (20%)
- **Bordas Ativas**: `border-white/30` (30%)
- **Backgrounds Overlay**: `bg-black/80` (80%)
- **Backgrounds Card**: `bg-zinc-950/50` (50%)

## 2. PADRÕES DE LAYOUT

### 2.1 Sistema de Grid

#### Container Principal
```css
max-w-7xl mx-auto px-6
```
- **Largura Máxima**: 1280px
- **Padding Horizontal**: 24px (1.5rem)

#### Grid de Seções
```css
grid md:grid-cols-2 gap-10
grid md:grid-cols-[280px_1fr] lg:grid-cols-[280px_1fr_240px] gap-8
```

#### Grid de Cards (Projetos)
```css
grid sm:grid-cols-2 lg:grid-cols-3 gap-5
```
- **Mobile**: 1 coluna
- **Tablet**: 2 colunas
- **Desktop**: 3 colunas
- **Gap**: 20px (1.25rem)

### 2.2 Espaçamentos Recorrentes

#### Padding Interno

| Elemento | Padding |
|----------|---------|
| **Seções** | `py-14` (56px vertical) |
| **Cards** | `p-5` (20px) |
| **Botões** | `px-4 py-2` (16px/8px) |
| **Inputs** | `px-3` (12px horizontal) |
| **Badges** | `px-3 py-1` (12px/4px) |
| **Modais** | `p-6` (24px) |

#### Margin/Gap

| Uso | Valor |
|-----|-------|
| **Gap entre cards** | `gap-3` (12px), `gap-4` (16px), `gap-5` (20px) |
| **Espaçamento vertical** | `space-y-4` (16px), `space-y-6` (24px) |
| **Gap de botões** | `gap-3` (12px) |

### 2.3 Breakpoints

| Nome | Valor | Uso |
|------|-------|-----|
| **sm** | 640px | Tablets pequenos |
| **md** | 768px | Tablets |
| **lg** | 1024px | Desktop |

### 2.4 Border Radius

| Elemento | Valor |
|----------|-------|
| **Cards** | `rounded-2xl` (16px), `rounded-3xl` (24px) |
| **Botões** | `rounded-2xl` (16px) |
| **Inputs** | `rounded-xl` (12px) |
| **Badges** | `rounded-full` (9999px) |
| **Ícones Container** | `rounded-lg` (8px) |

## 3. COMPONENTES REUTILIZÁVEIS

### 3.1 Button

#### Estrutura Base
```jsx
<Button variant="default" size="md">Texto</Button>
```

#### Variantes

| Variante | Classes | Uso |
|----------|---------|-----|
| **default** | `bg-white text-black border-white/10 hover:bg-zinc-100` | Ação primária |
| **outline** | `bg-transparent text-white border-white/20 hover:bg-white/5` | Ação secundária |
| **ghost** | `bg-transparent text-white border-transparent hover:bg-white/5` | Ação terciária |
| **secondary** | `bg-zinc-800 text-white border-white/10 hover:bg-zinc-700` | Alternativa |

#### Tamanhos

| Tamanho | Classes | Altura |
|---------|---------|--------|
| **md** | `h-10 px-4` | 40px |
| **sm** | `h-9 px-3` | 36px |
| **icon** | `h-12 w-12 p-2` | 48px |

#### Estados
- **Base**: `inline-flex items-center justify-center gap-2 rounded-2xl text-sm font-medium transition shadow-sm border`
- **Hover**: Definido por variante
- **Disabled**: Opacidade reduzida (implícito)

### 3.2 Card

#### Estrutura
```jsx
<Card>
  <CardHeader>
    <CardTitle>Título</CardTitle>
    <CardDescription>Descrição</CardDescription>
  </CardHeader>
  <CardContent>Conteúdo</CardContent>
  <CardFooter>Rodapé</CardFooter>
</Card>
```

#### Classes Base
- **Card**: `rounded-3xl border bg-zinc-950/50 border-white/10`
- **CardHeader**: `p-5 border-b border-white/5`
- **CardContent**: `p-5`
- **CardFooter**: `p-5 border-t border-white/5 flex items-center gap-3`
- **CardTitle**: `text-base font-semibold`
- **CardDescription**: `text-xs text-zinc-400`

#### Estados Visuais
- **Hover**: `hover:border-white/20`
- **Glow Roxo**: `felixo-card-glow` (animação de brilho)
- **Glow Branco**: `felixo-card-glow-white`
- **Glow Intenso**: `felixo-card-glow-intense`

### 3.3 Badge

#### Estrutura
```jsx
<Badge className="bg-purple-500/10 text-purple-400">Tag</Badge>
```

#### Classes Base
```css
inline-flex items-center rounded-full px-3 py-1 text-xs font-medium border border-white/10
```

#### Variações por Tecnologia
Usa função `getTagColor(tag)` para aplicar cores específicas.

### 3.4 Input

#### Estrutura
```jsx
<Input placeholder="Texto" />
```

#### Classes Base
```css
w-full h-10 rounded-xl bg-zinc-800/50 border border-white/10 px-3 text-sm text-white outline-none focus:ring-0
```

#### Estados
- **Focus**: `input-glowing-border:focus` (borda roxa com glow)
- **Placeholder**: `text-zinc-400`

### 3.5 Modal

#### Estrutura Base
```jsx
<motion.div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50">
  <motion.div className="border border-purple-500/30 rounded-2xl w-11/12 max-w-md p-6 shadow-2xl felixo-card-glow">
    {/* Conteúdo */}
  </motion.div>
</motion.div>
```

#### Características
- **Overlay**: `bg-black/80 backdrop-blur-sm`
- **Container**: `rounded-2xl border-purple-500/30 felixo-card-glow`
- **Largura**: `w-11/12 max-w-md` (responsivo)
- **Animação**: Framer Motion com fade in/out

## 4. PADRÕES DE INTERAÇÃO

### 4.1 Estados de Hover

| Elemento | Efeito |
|----------|--------|
| **Botões** | Mudança de background + shimmer effect |
| **Cards** | `hover:border-white/20` + scale sutil |
| **Links** | `hover:text-purple-400` ou `hover:text-white` |
| **Ícones Sociais** | `hover:scale-150` + cor roxa |
| **Tech Icons** | `hover:scale-150 hover:z-50 hover:shadow-[0_0_30px_rgba(255,255,255,0.3)]` |

### 4.2 Animações e Transições

#### Transições Padrão
```css
transition-all duration-300
transition-colors
transition-transform
```

#### Animações Customizadas

| Nome | Duração | Easing | Uso |
|------|---------|--------|-----|
| **title-glow** | 3s | ease-in-out | Brilho de títulos (verde) |
| **title-glow-purple** | 3s | ease-in-out | Brilho de títulos (roxo) |
| **title-glow-ts** | 3s | ease-in-out | Brilho de títulos (azul TS) |
| **title-glow-python** | 3s | ease-in-out | Brilho de títulos (azul Python) |
| **card-glow-breathe** | 3s | ease-in-out | Pulsação de cards (roxo) |
| **card-glow-breathe-white** | 3s | ease-in-out | Pulsação de cards (branco) |
| **card-glow-breathe-intense-hover** | 2.5s | ease-in-out | Pulsação intensa em hover |
| **text-glow-breathe** | 3.8s | ease-in-out | Pulsação de texto |
| **gradient-orbit** | 7.5s | linear | Movimento orbital de gradiente |
| **about-orbit-spin** | 6s / 8.5s | linear | Órbita ao redor da foto |
| **photo-glow-breathe** | 3s | ease-in-out | Brilho da foto de perfil |
| **tech-colors-cycle** | 25s | linear | Ciclo de cores das tecnologias |
| **glow-effect** | 3s | ease-in-out | Brilho branco pulsante |

#### Shimmer Effect (Botões)
```css
/* Brilho que passa da esquerda para direita */
.absolute.inset-0.-translate-x-full.group-hover:translate-x-[150%]
.transition-transform.duration-1000
.bg-gradient-to-r.from-transparent.via-white/20.to-transparent
```

### 4.3 Feedback Visual

#### Loading States
- Ícone `Wrench` para "Em Desenvolvimento"
- Ícone `CheckCircle2` para "Finalizado"

#### Scroll Behavior
```css
scroll-behavior: smooth;
scroll-padding-top: 80px;
```

#### Scrollbar Customizada
```css
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
::-webkit-scrollbar-thumb {
  background: rgba(74, 74, 74, 0.8);
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(106, 106, 106, 0.9);
}
```

### 4.4 Interações Especiais

#### Drag no Carrossel
- `cursor-grab` no estado normal
- `cursor-grabbing` durante o drag
- Momentum desabilitado: `dragMomentum={false}`

#### Grid de Projetos com Hover
- Card em hover: `felixo-card-glow-intense-hover`
- Cards adjacentes: `felixo-card-glow-subtle`
- Cards distantes: `opacity: 0.2` (faded)

#### Busca Interativa
- Animação `layoutId` para transição suave
- Overlay com `backdrop-blur-sm`
- Stagger animation nos resultados

## 5. PADRÕES TÉCNICOS

### 5.1 Convenções de Nomenclatura

#### Arquivos
- **Componentes**: `kebab-case.jsx` (ex: `portfolio-card.jsx`)
- **Seções**: `kebab-case.jsx` (ex: `hero.jsx`)
- **Utilitários**: `kebab-case.js` (ex: `utils.js`)

#### Classes CSS Customizadas
- **Prefixo Felixo**: `felixo-*` (ex: `felixo-card-glow`)
- **Prefixo About**: `about-*` (ex: `about-orbit`)
- **Estados**: `hover-*`, `animate-*`

#### Variáveis CSS
```css
--felixo-glow-intensity: 1;
--tech-glow-color: rgba(...);
```

### 5.2 Organização de Pastas

```
src/
├── assets/
│   ├── images/
│   └── readmes/
├── components/
│   ├── layout/      (navbar, footer)
│   ├── parts/       (portfolio-card)
│   └── ui/          (button, card, badge, input, modais)
├── data/            (projects.jsx)
├── pages/           (páginas específicas)
├── sections/        (seções da home)
├── utils/           (funções auxiliares)
├── App.jsx
├── index.css
└── main.jsx
```

### 5.3 Regras Implícitas de Design

#### Consistência de Brilho (Glow)
- **Roxo**: Marca Felixo, elementos principais
- **Branco**: Elementos secundários, alternativas
- **Cores de Tech**: Badges e títulos específicos

#### Hierarquia de Z-Index
- **Navbar**: `z-40`
- **Modais**: `z-50`
- **Partículas de Fundo**: `z-0` (implícito)
- **Conteúdo**: `z-10`

#### Responsividade
- **Mobile First**: Classes base sem prefixo
- **Breakpoints**: `md:`, `lg:` para ajustes
- **Grid Adaptativo**: 1 → 2 → 3 colunas

### 5.4 Funções Utilitárias

#### cx(...classes)
Combina classes condicionalmente, removendo valores falsy.

#### loop(arr)
Triplica array para carrossel infinito.

#### getTagColor(tag)
Retorna classes Tailwind baseadas na tecnologia.

#### felixoGlowIntensityStyle(percent)
Retorna objeto de estilo com intensidade customizada.

#### getFelixoGlowClass(percent)
Retorna classe utilitária de intensidade (25/50/75/100/150).

## 6. INCONSISTÊNCIAS E OPORTUNIDADES

### 6.1 Inconsistências Identificadas

1. **Border Radius Variável**
   - Cards usam `rounded-2xl` e `rounded-3xl` sem padrão claro
   - **Sugestão**: Padronizar `rounded-3xl` para cards grandes, `rounded-2xl` para cards pequenos

2. **Padding de Cards**
   - `p-5` (20px) é padrão, mas alguns usam `p-6` (24px)
   - **Sugestão**: Documentar quando usar cada um

3. **Animações de Glow**
   - Múltiplas variações similares (`card-glow-breathe`, `card-glow-breathe-intense`, etc.)
   - **Sugestão**: Consolidar em uma animação com variáveis CSS

4. **Nomenclatura de Cores**
   - `felixo-purple` vs `felixo-purple-bright` não é intuitivo
   - **Sugestão**: Renomear para `felixo-purple-400` e `felixo-purple-500` (seguindo padrão Tailwind)

### 6.2 Estilos Duplicados

1. **Gradientes de Fundo**
   - Múltiplos gradientes similares em diferentes seções
   - **Sugestão**: Criar classes utilitárias reutilizáveis

2. **Efeitos de Shimmer**
   - Código repetido em vários botões
   - **Sugestão**: Criar componente `ShimmerButton`

3. **Estrutura de Modal**
   - Overlay e container repetidos
   - **Sugestão**: Criar componente base `Modal` reutilizável

### 6.3 Melhorias Sugeridas

#### Tokens de Design
Criar arquivo de tokens centralizados:
```js
// design-tokens.js
export const colors = {
  brand: {
    purple: '#C084FC',
    purpleBright: '#A855F7',
  },
  // ...
};

export const spacing = {
  section: 'py-14',
  card: 'p-5',
  // ...
};
```

#### Sistema de Variantes
Expandir componentes com mais variantes:
- Button: adicionar `size="lg"` e `size="xs"`
- Card: adicionar variantes `elevated`, `flat`, `outlined`

#### Acessibilidade
- Adicionar `aria-label` em todos os botões de ícone
- Garantir contraste mínimo de 4.5:1 em textos
- Adicionar estados de `focus-visible` mais visíveis

#### Performance
- Usar `will-change` apenas em animações ativas
- Lazy load de imagens
- Code splitting por seção

#### Documentação de Componentes
Adicionar Storybook ou similar para visualizar todos os componentes isoladamente.

---

**Versão**: 1.0  
**Última Atualização**: 2024  
**Tecnologias**: React 18, Tailwind CSS 3, Framer Motion 10
