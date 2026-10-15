import { beforeEach, expect, test, vi } from "vitest";

beforeEach(() => {
  vi.resetModules();
});

test("busca e atualiza a conta do analista sem trocar o id", async () => {
  const { atualizarUsuario, buscarUsuarioPorId } = await import(
    "../../frontend/src/services/usuarioService"
  );

  const conta = buscarUsuarioPorId(1);

  expect(conta).toMatchObject({
    nome: "Ricardo",
    email: "ricardo.almeida@cerne.com",
    perfil: "analista",
  });

  const atualizado = atualizarUsuario(1, {
    nome: "Ricardo Souza",
    email: "ricardo.souza@cerne.com",
  });

  expect(atualizado).toMatchObject({
    id: 1,
    nome: "Ricardo Souza",
    email: "ricardo.souza@cerne.com",
    perfil: "analista",
  });
  expect(buscarUsuarioPorId(1)?.email).toBe("ricardo.souza@cerne.com");
});

test("nao atualiza conta inexistente", async () => {
  const { atualizarUsuario } = await import("../../frontend/src/services/usuarioService");

  expect(atualizarUsuario(999, { nome: "Ninguem" })).toBeUndefined();
});

test("cadastra analista ativo e permite excluir a conta", async () => {
  const { buscarUsuarioPorId, criarUsuario, excluirUsuario } = await import(
    "../../frontend/src/services/usuarioService"
  );

  const criado = criarUsuario({
    nome: "Carlos",
    sobrenome: "Souza",
    email: "carlos@email.com",
    cpf: "222.222.222-22",
    celular: "(51) 97777-7777",
    rua: "Rua B",
    numero: "20",
    bairro: "Centro",
    cep: "95700-010",
    cidade: "Bento Gonçalves",
    uf: "RS",
    perfil: "analista",
    status: "ativo",
  });

  expect(criado.perfil).toBe("analista");
  expect(criado.status).toBe("ativo");
  expect(buscarUsuarioPorId(criado.id)?.email).toBe("carlos@email.com");
  expect(excluirUsuario(criado.id)).toBe(true);
  expect(buscarUsuarioPorId(criado.id)).toBeUndefined();
  expect(excluirUsuario(criado.id)).toBe(false);
});
