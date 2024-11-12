#include "mlir/IR/Builders.h"
#include "mlir/IR/MLIRContext.h"
#include "mlir/IR/Operation.h"
#include "mlir/IR/Types.h"

#include "rust/cxx.h"

namespace tensat {
enum class Type : uint8_t;
enum class Ops : uint8_t;
struct Vector;
struct Matrix;
struct Tensor;
struct Node;
struct CppGraphConverter;

/**
 * Functions exposed to Rust (Tensat) for getting the cost of new operations.
 */

rust::Vec<uint64_t> get_cost(Ops op, rust::Vec<tensat::Tensor> operands,
                             rust::Vec<tensat::Vector> other_vector_args,
                             rust::Vec<int64_t> int_args,
                             rust::Vec<tensat::Matrix> matrix_args);

rust::Vec<Tensor> get_shape(Ops op, rust::Vec<tensat::Tensor> operands,
                            rust::Vec<tensat::Vector> other_vector_args,
                            rust::Vec<int64_t> int_args,
                            rust::Vec<tensat::Matrix> matrix_args);

rust::Box<CppGraphConverter>
apply_mlir_rewrite(rust::Vec<tensat::Node> nodes,
                   rust::Vec<tensat::Tensor> roots);

} // namespace tensat
