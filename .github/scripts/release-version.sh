#!/usr/bin/env bash
# Decide se uma tag de release é mais nova que outra — para não repetir o
# defeito medido no Felixo AI Core em 26/08/2026: uma release mais antiga
# terminou de publicar DEPOIS de uma mais nova já promovida, e marcar
# "Latest" só por ter rodado por último reverteria quem tivesse atualização
# automática ligada.
#
# Aqui a tag é escolhida por um committer ao empurrar `vX.Y.Z` (não gerada
# automaticamente), mas a mesma race pode acontecer: duas tags empurradas
# perto uma da outra, com os workflows terminando fora de ordem. `sort -V`
# entende ordem numérica de versão (v2.9 < v2.10), o que uma comparação de
# texto simples erraria.
set -u

# Verdadeiro quando $1 é mais nova que $2. Ausência de "atual" (string
# vazia) conta como "não há nada pra perder" — a candidata sempre vence.
is_tag_newer() {
  local candidata="$1" atual="$2"

  if [[ -z "$atual" ]]; then
    return 0
  fi
  if [[ "$candidata" == "$atual" ]]; then
    return 1
  fi

  local maior
  maior="$(printf '%s\n%s\n' "$candidata" "$atual" | sort -V | tail -n1)"
  [[ "$maior" == "$candidata" ]]
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  is_tag_newer "$@"
fi
