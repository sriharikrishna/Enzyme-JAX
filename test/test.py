from absl.testing import absltest
import jax
import jax.numpy as jnp
from enzyme_ad.jax import cpp_call, enzyme_jax_ir

argv = ("-I/usr/include/c++/11", "-I/usr/include/x86_64-linux-gnu/c++/11")


class EnzymeJax(absltest.TestCase):
    def test_custom_cpp_kernel(self):
        @jax.jit
        def do_something(ones):
            shape = jax.core.ShapedArray(ones.shape, ones.dtype)
            a, b = cpp_call(
                ones,
                out_shapes=[shape, shape],
                source="""
        template<std::size_t N, std::size_t M>
        void myfn(enzyme::tensor<float, N, M>& out0,
                  enzyme::tensor<float, N, M>& out1,
                  const enzyme::tensor<float, N, M>& in0) {
          for (int j=0; j<N; j++) {
            for (int k=0; k<M; k++) {
                out0[j][k] = in0[j][k] + 42;
            }
          }
          for (int j=0; j<2; j++) {
            for (int k=0; k<3; k++) {
                out1[j][k] = in0[j][k] + 2 * 42;
            }
          }
        }
        """,
                fn="myfn",
                argv=argv,
            )
            c = cpp_call(
                a,
                out_shapes=[jax.core.ShapedArray([4, 4], jnp.float32)],
                source="""
        template<typename T1, typename T2>
        void f(T1& out0, const T2& in1) {
          out0 = 56.0f;
        }
        """,
                argv=argv,
            )
            return a, b, c

        ones = jnp.ones((2, 3), jnp.float32)
        x, y, z = do_something(ones)

        print(x)
        print(y)
        print(z)

        # JVP
        primals, tangents = jax.jvp(do_something, (ones,), (ones,))
        print(primals)
        print(tangents)

        # VJP
        primals, f_vjp = jax.vjp(do_something, ones)
        (grads,) = f_vjp((x, y, z))
        print(primals)
        print(grads)

    def test_enzyme_mlir_jit(self):
        @jax.jit
        @enzyme_jax_ir(argv=argv)
        def add_one(x: jax.Array, y) -> jax.Array:
            return x + 1 + y

        # But it should print LLVM IR in the process.
        add_one(jnp.array([1.0, 2.0, 3.0]), jnp.array([10.0, 20.0, 30.0]))

        primals, tangents = jax.jvp(
            add_one,
            (jnp.array([1.0, 2.0, 3.0]), jnp.array([10.0, 20.0, 30.0])),
            (jnp.array([0.1, 0.2, 0.3]), jnp.array([50.0, 70.0, 110.0])),
        )
        print(primals)
        print(tangents)

        primals, f_vjp = jax.vjp(
            add_one, jnp.array([1.0, 2.0, 3.0]), jnp.array([10.0, 20.0, 30.0])
        )
        grads = f_vjp(jnp.array([500.0, 700.0, 110.0]))
        print(primals)
        print(grads)


if __name__ == "__main__":
    absltest.main()
