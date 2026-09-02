import assert from 'node:assert/strict'
import test from 'node:test'
import { isValidSoundCloudInput } from '../src/utils/validation.js'

test('aceita URL SoundCloud com ou sem protocolo', () => {
  assert.equal(isValidSoundCloudInput('https://soundcloud.com/artista'), true)
  assert.equal(isValidSoundCloudInput('soundcloud.com/artista/sets/album'), true)
})

test('aceita nome simples de perfil para o fluxo do CLI', () => {
  assert.equal(isValidSoundCloudInput('artista_01'), true)
})

test('rejeita domínio parecido e entrada vazia', () => {
  assert.equal(isValidSoundCloudInput('https://soundcloud.com.evil.example/artista'), false)
  assert.equal(isValidSoundCloudInput(''), false)
})
