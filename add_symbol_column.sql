-- Script para agregar la columna symbol a la tabla news_with_sentiment
-- Ejecutar este script si la tabla ya existe pero no tiene la columna symbol

-- Agregar la columna symbol si no existe
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'news_with_sentiment' 
        AND column_name = 'symbol'
    ) THEN
        ALTER TABLE news_with_sentiment ADD COLUMN symbol VARCHAR(10);
        RAISE NOTICE 'Columna symbol agregada a news_with_sentiment';
    ELSE
        RAISE NOTICE 'La columna symbol ya existe en news_with_sentiment';
    END IF;
END $$;

-- Verificar que la columna se agregó correctamente
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'news_with_sentiment' 
ORDER BY ordinal_position; 