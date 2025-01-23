import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class CalculatorTest {
    @Test
    void add_positiveIntegers_returnsCorrectResult() {
        Calculator calculator = new Calculator();
        int result = calculator.add(2, 3);
        assertEquals(5, result);
    }

    @Test
    void subtract_positiveIntegers_returnsCorrectResult() {
        Calculator calculator = new Calculator();
        int result = calculator.subtract(4, 2);
        assertEquals(2, result);
    }

    @Test
    void multiply_positiveIntegers_returnsCorrectResult() {
        Calculator calculator = new Calculator();
        int result = calculator.multiply(3, 4);
        assertEquals(12, result);
    }

    @Test
    void divide_positiveIntegers_returnsCorrectResult() {
        Calculator calculator = new Calculator();
        double result = calculator.divide(8, 2);
        assertEquals(4.0, result, 0.001);
    }

    @Test
    void divide_byZero_throwsIllegalArgumentException() {
        Calculator calculator = new Calculator();
        try {
            calculator.divide(8, 0);
            fail("Expected IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            assertTrue(e.getMessage().contains("Cannot divide by zero"));
        }
    }
}