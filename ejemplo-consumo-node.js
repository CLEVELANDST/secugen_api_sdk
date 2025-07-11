const axios = require('axios');

async function capturarHuella() {
    try {
        const response = await axios.post('http://localhost:5000/capturar-huella');
        const { data } = response;
        
        if (data.success) {
            // data.data.imagen contiene la imagen en base64
            // data.data.width y data.data.height contienen las dimensiones
            return data.data;
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error('Error al capturar huella:', error.message);
        throw error;
    }
} 